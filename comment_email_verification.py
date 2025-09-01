#!/usr/bin/env python3
"""
Simple script to comment out email verification functionality
"""

def comment_out_email_verification():
    with open('app/auth_api.py', 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    in_email_verification = False
    
    for i, line in enumerate(lines):
        # Check if we're entering email verification section
        if 'Email verification endpoints' in line:
            new_lines.append('# ' + line)
            in_email_verification = True
            continue
        
        # Check if we're exiting email verification section (next endpoint)
        if in_email_verification and ('@router.post("/login"' in line or '@router.get("/login"' in line):
            in_email_verification = False
        
        # Comment out lines in email verification section
        if in_email_verification:
            if line.strip() and not line.startswith('#'):
                new_lines.append('# ' + line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Comment out VERIFICATION_STATE variable
    for i, line in enumerate(new_lines):
        if 'VERIFICATION_STATE: Dict[int, dict] = {}' in line:
            new_lines[i] = '# ' + line + '  # DISABLED FOR NOW\n'
    
    # Comment out email_verified and is_verified lines in Google OAuth
    for i, line in enumerate(new_lines):
        if 'email_verified = info.get("email_verified")' in line:
            new_lines[i] = '    # ' + line.strip() + '  # DISABLED FOR NOW\n'
        elif 'is_verified=bool(email_verified)' in line:
            new_lines[i] = '        # ' + line.strip() + '  # DISABLED FOR NOW\n'
    
    # Write back to file
    with open('app/auth_api.py', 'w') as f:
        f.writelines(new_lines)
    
    print("Email verification functionality has been commented out in auth_api.py")

if __name__ == "__main__":
    comment_out_email_verification()
