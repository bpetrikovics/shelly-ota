import sys
import os
import logging
import yaml


AUTH_NONE = 0
AUTH_SINGLE = 1
AUTH_MULTI=2


class AuthProvider:
    def __init__(self, args):
        if args.auth_env and args.auth_file:
            logger.critical("Cannot specify both auth_env and auth_file, exiting")
            sys.exit(-1)
        
        self.auth_mode = AUTH_NONE
        
        if args.auth_env:
            logger.debug("Auth mode is Single User/Pass, via env variable %s", args.auth_env)
            auth_env = os.getenv(args.auth_env)
            try:
                self.auth_user, self.auth_pass = auth_env.split(':')
            except Exception as exc:
                logger.exception(exc)
                self.auth_mode = AUTH_NONE
                logger.error("Cannot retrieve auth credentials from environment, defaulting to no auth")
            if self.auth_user and self.auth_pass:
                logger.debug("Will authenticate as user %s", self.auth_user)
                self.auth_mode = AUTH_SINGLE

        elif args.auth_file:
            logger.debug(f"Auth mode is File/Rule based, loading from {args.auth_file}")
            self.auth_mode = AUTH_MULTI
            try:
                with open(args.auth_file, 'r') as rule_file:
                    self.auth_rules = yaml.safe_load(rule_file.read()).get('auth')
            except Exception as exc:
                logger.error("Unable to load auth rules: %s", exc)
                sys.exit(-1)

    def get_auth_for(self, device):
        if self.auth_mode == AUTH_NONE:
            return None
        
        if self.auth_mode == AUTH_SINGLE:
            return (self.auth_user, self.auth_pass)

        if self.auth_mode == AUTH_MULTI:
            for rule in self.auth_rules:
                if not rule.get('creds') or not rule.get('match'):
                    continue

                match_type = rule['match']
                match_value = rule.get(match_type, None)

                if not match_value:
                    continue

                if hasattr(device, match_type):
                    attr = getattr(device, match_type)
                    if attr == match_value:
                        return (rule['creds'].get('user'), rule['creds'].get('pass'))

            return None


logger = logging.getLogger(__name__)
