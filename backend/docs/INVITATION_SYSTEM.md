# Household Invitation System

## Overview
Secure invitation system allowing users to invite their partner to join their "mission" or "operation" (household budget).

## How It Works

### 1. User A Invites User B

**Endpoint**: `POST /api/households/{household_id}/invite`

**Request**:
```json
{
  "email": "partner@example.com"
}
```

**Response**:
```json
{
  "message": "Invitation sent successfully",
  "invite": {
    "id": 1,
    "household_id": 5,
    "household_name": "Smith Family",
    "inviter_name": "Alice",
    "invitee_email": "bob@example.com",
    "status": "pending",
    "expires_at": "2025-11-13T10:30:00Z"
  },
  "invite_url": "/join-household/abc123def456...",
  "note": "Share this link with your partner to join the operation"
}
```

### 2. User B Checks Invite Details

**Endpoint**: `GET /api/households/invites/{token}`

Shows who's inviting them and to which household before they accept.

**Response**:
```json
{
  "id": 1,
  "household_name": "Smith Family",
  "inviter_name": "Alice",
  "invitee_email": "bob@example.com",
  "status": "pending",
  "created_at": "2025-11-06T10:30:00Z",
  "expires_at": "2025-11-13T10:30:00Z"
}
```

### 3. User B Accepts Invite

**Endpoint**: `POST /api/households/invites/{token}/accept`

**Response**:
```json
{
  "message": "Welcome to the operation! You've successfully joined the household.",
  "household": {
    "id": 5,
    "name": "Smith Family",
    "members": [
      {
        "id": 1,
        "name": "Alice",
        "role": "owner"
      },
      {
        "id": 2,
        "name": "Bob",
        "role": "member"
      }
    ]
  }
}
```

### 4. Now Both Users See Everything!

Both Alice and Bob now see:
- ✅ All Funds
- ✅ All Bills
- ✅ All Income
- ✅ All Bank Accounts (with owner labels)
- ✅ All Transactions (with creator labels)
- ✅ All Debts (with owner labels)

## Security Features

### Token-Based Invites
- Unique 32-character secure random token
- Cannot be guessed or brute-forced
- Single-use (marked as accepted/rejected after use)

### Email Verification
- Invite is tied to specific email address
- User must be logged in with matching email to accept
- Prevents wrong person from accepting

### Expiration
- Invites expire after 7 days
- Expired invites are marked and cannot be accepted
- New invite needed if expired

### Status Tracking
- **pending**: Invite sent, awaiting response
- **accepted**: User joined household
- **rejected**: User declined invite
- **expired**: Invite expired (7+ days old)

## API Routes Summary

### Household Management
- `GET /api/households/` - List user's households
- `GET /api/households/{id}` - Get household details
- `POST /api/households/` - Create new household
- `PUT /api/households/{id}` - Update household (owner only)
- `DELETE /api/households/{id}` - Delete household (owner only)

### Invitation Flow
- `POST /api/households/{id}/invite` - Send invite
- `GET /api/households/invites/{token}` - View invite details
- `POST /api/households/invites/{token}/accept` - Accept invite
- `POST /api/households/invites/{token}/reject` - Reject invite

### Membership Management
- `DELETE /api/households/{id}/members/{user_id}` - Remove member (owner only)
- `POST /api/households/{id}/leave` - Leave household (member only)
- `POST /api/households/{id}/switch` - Switch default household

## Example User Flow

### Alice's Side (Inviter)
```
1. Alice logs in → automatically has "Alice's Household"
2. Alice goes to Settings → Household Management
3. Clicks "Invite Partner"
4. Enters Bob's email: bob@example.com
5. Gets invite link: /join-household/abc123...
6. Shares link with Bob (text, email, etc.)
```

### Bob's Side (Invitee)
```
1. Bob creates account with bob@example.com
2. Bob clicks the invite link Alice sent
3. Sees: "Alice invites you to join Smith Family"
4. Clicks "Accept Invitation"
5. Now sees all of Alice's funds, bills, accounts!
```

## Permission Model

### Owner (Creator)
- Can invite members
- Can remove members
- Can update household name
- Can delete household
- Cannot leave (must transfer ownership first)

### Member (Invited)
- Can invite other members
- Can view/edit all household data
- Can leave anytime
- Cannot remove other members
- Cannot delete household

### Both Roles
- Full access to all funds, bills, accounts, transactions
- Can create/edit/delete any household resource
- Complete transparency and trust

## Frontend Integration Points

### Settings Page - Household Section
```jsx
- Display current household name
- Show list of members with roles
- "Invite Partner" button → opens invite modal
- Copy invite link to clipboard
- List pending invites
```

### Header
```jsx
- Show household indicator: "Smith Family (2 members)"
- Show partner's name/avatar
- Quick household switcher (if user belongs to multiple)
```

### Resource Labels
```jsx
// Accounts page
"Bob's Chase Checking" (owner_name from API)

// Transactions list  
"Grocery Store - $125" (created by Alice)

// Debts page
"Alice's Car Loan" (owner_name from API)
```

## Testing Scenarios

1. **Single User**: Alice creates account → gets default household
2. **Invite Flow**: Alice invites Bob → Bob accepts
3. **Complete Transparency**: Both see all funds/accounts/transactions
4. **Owner Labels**: UI shows "Bob's account" but Alice can see it
5. **Creator Labels**: Transaction shows "created by Bob"
6. **Leave Household**: Bob leaves → no longer sees Alice's data
7. **Remove Member**: Alice removes Bob → same result
8. **Expired Invite**: Wait 7 days → invite cannot be accepted

## Notes

- Users automatically get a default household on signup (backwards compatible)
- Single users work exactly as before
- Invites are optional - not required for single-user workflow
- User can belong to multiple households (future feature)
- Currently set up for couples, but architecture supports families (3+ members)
