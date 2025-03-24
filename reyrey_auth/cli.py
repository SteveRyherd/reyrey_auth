"""
Command-line interface for Reynolds & Reynolds Authentication
"""

import argparse
import sys
from .auth import get_token, save_token, check_token_validity

def main():
    """Main entry point for the command-line interface"""
    parser = argparse.ArgumentParser(description="Reynolds & Reynolds Authentication CLI")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Get token command
    get_parser = subparsers.add_parser('get', help='Get the current token')
    get_parser.add_argument('--name', default='DRT', help='Token name (default: DRT)')
    get_parser.add_argument('--check', action='store_true', help='Check token validity')
    
    # Set token command
    set_parser = subparsers.add_parser('set', help='Set a token value')
    set_parser.add_argument('token', help='Token value to set')
    set_parser.add_argument('--name', default='DRT', help='Token name (default: DRT)')
    set_parser.add_argument('--domain', default='focus.dealer.reyrey.net', 
                           help='Domain (default: focus.dealer.reyrey.net)')
    
    # Check token command
    check_parser = subparsers.add_parser('check', help='Check if a token is valid')
    check_parser.add_argument('--name', default='DRT', help='Token name (default: DRT)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command is specified, show help
    if not args.command:
        parser.print_help()
        return
    
    # Handle commands
    if args.command == 'get':
        token = get_token(token_name=args.name, check_token=args.check)
        if token:
            print(token)
        else:
            print(f"No token found for {args.name}")
            sys.exit(1)
    
    elif args.command == 'set':
        result = save_token(args.token, token_name=args.name, domain=args.domain)
        if result:
            print(f"Token successfully saved: {args.token[:10]}...")
        else:
            print("Failed to save token")
            sys.exit(1)
    
    elif args.command == 'check':
        token = get_token(token_name=args.name, check_token=False)
        if not token:
            print(f"No token found for {args.name}")
            sys.exit(1)
        
        is_valid = check_token_validity(token, token_name=args.name)
        if is_valid:
            print(f"Token for {args.name} is valid")
        else:
            print(f"Token for {args.name} is invalid or expired")
            sys.exit(1)

if __name__ == "__main__":
    main()
