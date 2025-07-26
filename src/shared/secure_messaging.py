"""Secure messaging for cross-VM encrypted communication."""

import json
import logging
import base64
from typing import Dict, Optional, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import secrets

logger = logging.getLogger(__name__)


class SecureMessaging:
    """Handle encrypted messaging between VMs with signature verification."""
    
    def __init__(self, key_manager):
        self.key_manager = key_manager
        self.development_mode = os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
    
    def create_secure_message(self, 
                            recipient_id: str,
                            message_type: str,
                            payload: Dict,
                            recipient_public_key: Optional[str] = None) -> Dict:
        """Create an encrypted and signed message for cross-VM communication."""
        try:
            # Create message structure
            message = {
                "sender_id": os.getenv('AGENT_ID', 'unknown'),
                "recipient_id": recipient_id,
                "message_type": message_type,
                "timestamp": self._get_timestamp(),
                "nonce": secrets.token_hex(16),
                "payload": payload
            }
            
            # Serialize message
            message_json = json.dumps(message, sort_keys=True)
            
            # Sign the message
            signature = self.key_manager.sign_message(message_json)
            
            # Encrypt if recipient public key provided
            if recipient_public_key:
                encrypted_payload = self._encrypt_payload(message_json)
                
                secure_message = {
                    "encrypted": True,
                    "encrypted_payload": encrypted_payload,
                    "signature": signature,
                    "sender_public_key": self.key_manager.get_public_key_pem(),
                    "sender_fingerprint": self.key_manager.get_key_fingerprint()
                }
            else:
                # Unencrypted but signed
                secure_message = {
                    "encrypted": False,
                    "message": message,
                    "signature": signature,
                    "sender_public_key": self.key_manager.get_public_key_pem(),
                    "sender_fingerprint": self.key_manager.get_key_fingerprint()
                }
            
            if self.development_mode:
                logger.debug(f"Created secure message for {recipient_id}")
            
            return secure_message
            
        except Exception as e:
            logger.error(f"Failed to create secure message: {e}")
            raise
    
    def verify_secure_message(self, secure_message: Dict) -> Tuple[bool, Optional[Dict]]:
        """Verify and decrypt a secure message."""
        try:
            # Extract components
            signature = secure_message.get("signature")
            sender_public_key = secure_message.get("sender_public_key")
            
            if not signature or not sender_public_key:
                return False, {"error": "Missing signature or public key"}
            
            # Handle encrypted messages
            if secure_message.get("encrypted"):
                # Decrypt payload
                decrypted_json = self._decrypt_payload(secure_message["encrypted_payload"])
                if not decrypted_json:
                    return False, {"error": "Failed to decrypt message"}
                
                message = json.loads(decrypted_json)
                message_json = decrypted_json
            else:
                # Unencrypted message
                message = secure_message.get("message")
                if not message:
                    return False, {"error": "Missing message content"}
                
                message_json = json.dumps(message, sort_keys=True)
            
            # Verify signature
            if not self.key_manager.verify_signature(message_json, signature, sender_public_key):
                return False, {"error": "Invalid signature"}
            
            # Verify timestamp freshness (5 minute window)
            if not self._verify_timestamp(message.get("timestamp")):
                return False, {"error": "Message timestamp too old"}
            
            # Verify nonce uniqueness (in production, would check against cache)
            # For now, just ensure it exists
            if not message.get("nonce"):
                return False, {"error": "Missing message nonce"}
            
            if self.development_mode:
                logger.debug(f"Verified secure message from {message.get('sender_id')}")
            
            return True, message
            
        except Exception as e:
            logger.error(f"Failed to verify secure message: {e}")
            return False, {"error": str(e)}
    
    def _encrypt_payload(self, plaintext: str) -> str:
        """Encrypt payload using AES-256-GCM."""
        try:
            # Generate random key and IV
            key = secrets.token_bytes(32)  # 256-bit key
            iv = secrets.token_bytes(12)    # 96-bit IV for GCM
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Encrypt
            ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
            
            # Package encrypted data
            encrypted_data = {
                "key": base64.b64encode(key).decode(),
                "iv": base64.b64encode(iv).decode(),
                "ciphertext": base64.b64encode(ciphertext).decode(),
                "tag": base64.b64encode(encryptor.tag).decode()
            }
            
            return base64.b64encode(json.dumps(encrypted_data).encode()).decode()
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def _decrypt_payload(self, encrypted_payload: str) -> Optional[str]:
        """Decrypt payload using AES-256-GCM."""
        try:
            # Decode encrypted data
            encrypted_data = json.loads(base64.b64decode(encrypted_payload))
            
            key = base64.b64decode(encrypted_data["key"])
            iv = base64.b64decode(encrypted_data["iv"])
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            tag = base64.b64decode(encrypted_data["tag"])
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext.decode()
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def _get_timestamp(self) -> str:
        """Get current UTC timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def _verify_timestamp(self, timestamp: str, max_age_seconds: int = 300) -> bool:
        """Verify timestamp is within acceptable age."""
        try:
            from datetime import datetime
            
            # Parse timestamp
            if timestamp.endswith('Z'):
                timestamp = timestamp[:-1] + '+00:00'
            
            msg_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            current_time = datetime.utcnow().replace(tzinfo=msg_time.tzinfo)
            
            # Check age
            age = (current_time - msg_time).total_seconds()
            return 0 <= age <= max_age_seconds
            
        except Exception as e:
            logger.error(f"Timestamp verification failed: {e}")
            return False
    
    def create_collaboration_request(self,
                                   target_agent: str,
                                   task_description: str,
                                   context: Dict,
                                   data_requirements: list) -> Dict:
        """Create a standardized collaboration request message."""
        payload = {
            "task_description": task_description,
            "context": context,
            "data_requirements": data_requirements,
            "priority": context.get("priority", "normal"),
            "timeout_seconds": context.get("timeout", 60)
        }
        
        return self.create_secure_message(
            recipient_id=target_agent,
            message_type="collaboration_request",
            payload=payload
        )
    
    def create_collaboration_response(self,
                                    request_id: str,
                                    result: Dict,
                                    status: str = "completed") -> Dict:
        """Create a standardized collaboration response message."""
        payload = {
            "request_id": request_id,
            "status": status,
            "result": result,
            "processing_time_ms": result.get("processing_time_ms", 0),
            "confidence_score": result.get("confidence_score", 0.0)
        }
        
        return self.create_secure_message(
            recipient_id=result.get("requester_id", "hub"),
            message_type="collaboration_response",
            payload=payload
        )