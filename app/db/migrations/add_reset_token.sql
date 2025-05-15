-- Add reset_token column to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255);

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_reset_token ON users(reset_token);

-- Add index for verification token if it doesn't exist
CREATE INDEX IF NOT EXISTS idx_users_verification_token ON users(verification_token); 