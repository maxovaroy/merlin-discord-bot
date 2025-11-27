import json
import os
import aiofiles
import asyncio
from datetime import datetime
from typing import Dict, List
import logging
from config import Config

logger = logging.getLogger(__name__)

class DataStorage:
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataStorage, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            # Core Systems
            self.muted_users: Dict[str, Dict] = {}
            self.warnings: Dict[str, Dict] = {}
            self.user_levels: Dict[str, Dict] = {}
            self.auto_reply_mutes: Dict[str, List[int]] = {}
            
            # Social System
            self.marriages: Dict[str, Dict] = {}
            self.children: Dict[str, Dict] = {}
            self.friends: Dict[str, Dict] = {}
            self.reputation: Dict[str, Dict] = {}
            self.gifts: Dict[str, Dict] = {}
            
            # Profile System  
            self.user_profiles: Dict[str, Dict] = {}
            self.achievements: Dict[str, Dict] = {}
            self.backgrounds: Dict[str, Dict] = {}
            
            self.initialized = True
            asyncio.create_task(self.load_data_async())
    
    async def load_data_async(self):
        """Load all bot data from JSON file"""
        async with self._lock:
            if os.path.exists(Config.DATA_FILE):
                try:
                    async with aiofiles.open(Config.DATA_FILE, 'r') as f:
                        content = await f.read()
                        data = json.loads(content)
                        # Load all data sections
                        self.muted_users = data.get('muted_users', {})
                        self.warnings = data.get('warnings', {})
                        self.user_levels = data.get('user_levels', {})
                        self.auto_reply_mutes = data.get('auto_reply_mutes', {})
                        self.marriages = data.get('marriages', {})
                        self.children = data.get('children', {})
                        self.friends = data.get('friends', {})
                        self.reputation = data.get('reputation', {})
                        self.gifts = data.get('gifts', {})
                        self.user_profiles = data.get('user_profiles', {})
                        self.achievements = data.get('achievements', {})
                        self.backgrounds = data.get('backgrounds', {})
                    logger.info("✅ Bot data loaded successfully")
                except Exception as e:
                    logger.error(f"❌ Error loading data: {e}")
                    # Reset all data on error
                    self._reset_all_data()
            else:
                logger.info("📁 No existing data file, starting fresh")
    
    async def save_data_async(self):
        """Save all bot data to JSON file"""
        async with self._lock:
            try:
                # 🚀 FIX: Only create directory if DATA_FILE has a path
                data_file_dir = os.path.dirname(Config.DATA_FILE)
                if data_file_dir:  # Only create directory if path exists
                    os.makedirs(data_file_dir, exist_ok=True)
                
                data = {
                    'muted_users': self.muted_users,
                    'warnings': self.warnings,
                    'user_levels': self.user_levels,
                    'auto_reply_mutes': self.auto_reply_mutes,
                    'marriages': self.marriages,
                    'children': self.children,
                    'friends': self.friends,
                    'reputation': self.reputation,
                    'gifts': self.gifts,
                    'user_profiles': self.user_profiles,
                    'achievements': self.achievements,
                    'backgrounds': self.backgrounds,
                }
                async with aiofiles.open(Config.DATA_FILE, 'w') as f:
                    await f.write(json.dumps(data, indent=2))
                logger.info("💾 Bot data saved successfully")
            except Exception as e:
                logger.error(f"❌ Error saving data: {e}")

    def _reset_all_data(self):
        """Reset all data dictionaries"""
        self.muted_users = {}
        self.warnings = {}
        self.user_levels = {}
        self.auto_reply_mutes = {}
        self.marriages = {}
        self.children = {}
        self.friends = {}
        self.reputation = {}
        self.gifts = {}
        self.user_profiles = {}
        self.achievements = {}
        self.backgrounds = {}

    # PROFILE METHODS
    def get_user_profile(self, user_id: int, server_id: int) -> Dict:
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key not in self.user_profiles:
            self.user_profiles[server_key] = {}
        
        if user_key not in self.user_profiles[server_key]:
            self.user_profiles[server_key][user_key] = {
                'bio': 'No bio set yet...',
                'title': 'Newcomer',
                'color': None,
                'banner': 'assassin',  # ✅ CHANGED to banner
                'badges': [],
                'profile_views': 0,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        
        return self.user_profiles[server_key][user_key]

    def update_user_profile(self, user_id: int, server_id: int, updates: Dict):
        """Update user profile and auto-save"""
        profile = self.get_user_profile(user_id, server_id)
        profile.update(updates)
        profile['last_updated'] = datetime.now().isoformat()
        asyncio.create_task(self.save_data_async())

    def increment_profile_views(self, user_id: int, server_id: int):
        """Increment profile view count"""
        profile = self.get_user_profile(user_id, server_id)
        profile['profile_views'] = profile.get('profile_views', 0) + 1
        asyncio.create_task(self.save_data_async())

    # ACHIEVEMENT METHODS
    def add_achievement(self, user_id: int, server_id: int, achievement_id: str, achievement_data: Dict):
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key not in self.achievements:
            self.achievements[server_key] = {}
        
        if user_key not in self.achievements[server_key]:
            self.achievements[server_key][user_key] = []
        
        # Check if achievement already exists
        existing_ids = [a.get('id') for a in self.achievements[server_key][user_key]]
        if achievement_id not in existing_ids:
            achievement = {
                'id': achievement_id,
                'name': achievement_data.get('name', 'Unknown'),
                'description': achievement_data.get('description', ''),
                'icon': achievement_data.get('icon', '🏆'),
                'unlocked_at': datetime.now().isoformat(),
                'rarity': achievement_data.get('rarity', 'common')
            }
            self.achievements[server_key][user_key].append(achievement)
            asyncio.create_task(self.save_data_async())
            return True
        return False

    def get_achievements(self, user_id: int, server_id: int):
        server_key = str(server_id)
        user_key = str(user_id)
        return self.achievements.get(server_key, {}).get(user_key, [])

    # BANNER METHODS - NEW SYSTEM
    def unlock_banner(self, user_id: int, server_id: int, banner_id: str, banner_name: str):
        """Unlock a banner for a user"""
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key not in self.backgrounds:  # Keep using backgrounds storage for compatibility
            self.backgrounds[server_key] = {}
        
        if user_key not in self.backgrounds[server_key]:
            self.backgrounds[server_key][user_key] = []
        
        # Check if banner already unlocked
        existing_ids = [bg.get('id') for bg in self.backgrounds[server_key][user_key]]
        if banner_id not in existing_ids:
            banner_data = {
                'id': banner_id,
                'name': banner_name,
                'unlocked_at': datetime.now().isoformat()
            }
            self.backgrounds[server_key][user_key].append(banner_data)
            asyncio.create_task(self.save_data_async())
            return True
        return False

    def get_banners(self, user_id: int, server_id: int):
        """Get user's unlocked banners"""
        server_key = str(server_id)
        user_key = str(user_id)
        
        if (server_key in self.backgrounds and 
            user_key in self.backgrounds[server_key]):
            return self.backgrounds[server_key][user_key]
        return []

    def has_banner(self, user_id: int, server_id: int, banner_id: str) -> bool:
        """Check if user has a specific banner unlocked"""
        user_banners = self.get_banners(user_id, server_id)
        banner_ids = [bg.get('id') for bg in user_banners]
        return banner_id in banner_ids or banner_id == 'assassin'  # Default banner

    def update_user_banner(self, user_id: int, server_id: int, banner_id: str):
        """Update user banner"""
        profile = self.get_user_profile(user_id, server_id)
        profile['banner'] = banner_id
        asyncio.create_task(self.save_data_async())

    # BACKWARD COMPATIBILITY - Keep old background methods working
    def unlock_background(self, user_id: int, server_id: int, background_id: str, background_name: str):
        """Alias for unlock_banner - for backward compatibility"""
        return self.unlock_banner(user_id, server_id, background_id, background_name)

    def get_backgrounds(self, user_id: int, server_id: int):
        """Alias for get_banners - for backward compatibility"""
        return self.get_banners(user_id, server_id)

    def has_background(self, user_id: int, server_id: int, background_id: str) -> bool:
        """Alias for has_banner - for backward compatibility"""
        return self.has_banner(user_id, server_id, background_id)

    # SOCIAL DATA METHODS
    def get_marriage(self, user_id: int, server_id: int):
        """Get marriage data for user"""
        server_key = str(server_id)
        user_key = str(user_id)
        return self.marriages.get(server_key, {}).get(user_key)

    def get_friends(self, user_id: int, server_id: int):
        """Get friends list for user"""
        server_key = str(server_id)
        user_key = str(user_id)
        
        if (server_key in self.friends and 
            user_key in self.friends[server_key]):
            return self.friends[server_key][user_key]
        return []

    def get_friends_count(self, user_id: int, server_id: int) -> int:
        """Get number of friends"""
        return len(self.get_friends(user_id, server_id))

    def get_reputation(self, user_id: int, server_id: int):
        """Get reputation points"""
        server_key = str(server_id)
        user_key = str(user_id)
        return self.reputation.get(server_key, {}).get(user_key, 0)

    def get_gifts(self, user_id: int, server_id: int):
        """Get gifts count"""
        server_key = str(server_id)
        user_key = str(user_id)
        return self.gifts.get(server_key, {}).get(user_key, 0)

    def get_children(self, user_id: int, server_id: int):
        """Get children data"""
        server_key = str(server_id)
        user_key = str(user_id)
        return self.children.get(server_key, {}).get(user_key, [])

    def get_children_count(self, user_id: int, server_id: int) -> int:
        """Get number of children"""
        return len(self.get_children(user_id, server_id))

    # MARRIAGE METHODS
    def add_marriage(self, user1_id: int, user2_id: int, server_id: int):
        server_key = str(server_id)
        if server_key not in self.marriages:
            self.marriages[server_key] = {}
        
        timestamp = datetime.now().isoformat()
        self.marriages[server_key][str(user1_id)] = {
            'partner': user2_id,
            'married_at': timestamp,
            'partner_name': f"User_{user2_id}"
        }
        self.marriages[server_key][str(user2_id)] = {
            'partner': user1_id,
            'married_at': timestamp,
            'partner_name': f"User_{user1_id}"
        }
        asyncio.create_task(self.save_data_async())

    def remove_marriage(self, user_id: int, server_id: int):
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key in self.marriages and user_key in self.marriages[server_key]:
            partner_id = self.marriages[server_key][user_key]['partner']
            del self.marriages[server_key][user_key]
            if str(partner_id) in self.marriages[server_key]:
                del self.marriages[server_key][str(partner_id)]
            asyncio.create_task(self.save_data_async())
            return partner_id
        return None

    def is_married(self, user_id: int, server_id: int) -> bool:
        return self.get_marriage(user_id, server_id) is not None

    # CHILDREN METHODS
    def add_child(self, parent_id: int, child_name: str, server_id: int):
        server_key = str(server_id)
        parent_key = str(parent_id)
        
        if server_key not in self.children:
            self.children[server_key] = {}
        
        if parent_key not in self.children[server_key]:
            self.children[server_key][parent_key] = []
        
        child_data = {
            'name': child_name,
            'adopted_at': datetime.now().isoformat(),
            'level': 1,
            'happiness': 100
        }
        
        self.children[server_key][parent_key].append(child_data)
        asyncio.create_task(self.save_data_async())

    # FRIEND METHODS
    def add_friend(self, user_id: int, friend_id: int, server_id: int):
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key not in self.friends:
            self.friends[server_key] = {}
        
        if user_key not in self.friends[server_key]:
            self.friends[server_key][user_key] = []
        
        if friend_id not in self.friends[server_key][user_key]:
            self.friends[server_key][user_key].append(friend_id)
            asyncio.create_task(self.save_data_async())

    def remove_friend(self, user_id: int, friend_id: int, server_id: int):
        server_key = str(server_id)
        user_key = str(user_id)
        
        if (server_key in self.friends and 
            user_key in self.friends[server_key] and 
            friend_id in self.friends[server_key][user_key]):
            
            self.friends[server_key][user_key].remove(friend_id)
            asyncio.create_task(self.save_data_async())

    # REPUTATION METHODS
    def add_reputation(self, user_id: int, server_id: int, points: int = 1):
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key not in self.reputation:
            self.reputation[server_key] = {}
        
        if user_key not in self.reputation[server_key]:
            self.reputation[server_key][user_key] = 0
        
        self.reputation[server_key][user_key] += points
        asyncio.create_task(self.save_data_async())
        return self.reputation[server_key][user_key]

    # GIFT METHODS
    def add_gift(self, user_id: int, server_id: int):
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key not in self.gifts:
            self.gifts[server_key] = {}
        
        if user_key not in self.gifts[server_key]:
            self.gifts[server_key][user_key] = 0
        
        self.gifts[server_key][user_key] += 1
        asyncio.create_task(self.save_data_async())
        return self.gifts[server_key][user_key]

    # AUTO-REPLY MUTE METHODS
    def mute_auto_reply(self, user_id: int, server_id: int):
        server_key = str(server_id)
        if server_key not in self.auto_reply_mutes:
            self.auto_reply_mutes[server_key] = []
        
        if user_id not in self.auto_reply_mutes[server_key]:
            self.auto_reply_mutes[server_key].append(user_id)
            asyncio.create_task(self.save_data_async())
    
    def unmute_auto_reply(self, user_id: int, server_id: int):
        server_key = str(server_id)
        if server_key in self.auto_reply_mutes and user_id in self.auto_reply_mutes[server_key]:
            self.auto_reply_mutes[server_key].remove(user_id)
            asyncio.create_task(self.save_data_async())
    
    def is_auto_reply_muted(self, user_id: int, server_id: int) -> bool:
        server_key = str(server_id)
        return (server_key in self.auto_reply_mutes and 
                user_id in self.auto_reply_mutes[server_key])
    
    # WARNING METHODS
    def add_warning(self, user_id: int, server_id: int, reason: str):
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key not in self.warnings:
            self.warnings[server_key] = {}
        
        if user_key not in self.warnings[server_key]:
            self.warnings[server_key][user_key] = []
        
        self.warnings[server_key][user_key].append({
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        asyncio.create_task(self.save_data_async())
    
    def get_warnings(self, user_id: int, server_id: int):
        server_key = str(server_id)
        user_key = str(user_id)
        return self.warnings.get(server_key, {}).get(user_key, [])
    
    def clear_warnings(self, user_id: int, server_id: int):
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key in self.warnings and user_key in self.warnings[server_key]:
            del self.warnings[server_key][user_key]
            asyncio.create_task(self.save_data_async())
    
    # MUTE USER METHODS
    def add_muted_user(self, user_id: int, server_id: int, duration: int = None):
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key not in self.muted_users:
            self.muted_users[server_key] = {}
        
        self.muted_users[server_key][user_key] = {
            'muted_at': datetime.now().isoformat(),
            'duration': duration,
            'unmute_at': (datetime.now().timestamp() + duration) if duration else None
        }
        asyncio.create_task(self.save_data_async())
    
    def remove_muted_user(self, user_id: int, server_id: int):
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key in self.muted_users and user_key in self.muted_users[server_key]:
            del self.muted_users[server_key][user_key]
            asyncio.create_task(self.save_data_async())
    
    def is_user_muted(self, user_id: int, server_id: int) -> bool:
        server_key = str(server_id)
        user_key = str(user_id)
        return (server_key in self.muted_users and 
                user_key in self.muted_users[server_key])
    
    def get_muted_users(self, server_id: int) -> Dict:
        server_key = str(server_id)
        return self.muted_users.get(server_key, {})