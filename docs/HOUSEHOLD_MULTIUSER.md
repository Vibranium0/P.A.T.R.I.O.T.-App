# Multi-User Household Support Implementation

## Overview
This document outlines the implementation of multi-user household support, allowing couples to share the same budget while maintaining individual accounts.

## Concept

### Complete Transparency - ALL Resources Shared (Household-level)
Everything is shared at the household level for complete trust and transparency:
- **Funds**: All household members see and can manage the same funds
- **Bills**: Shared bills visible to all household members
- **Income**: Household income tracking (contributed by either partner)
- **Bank Accounts**: All accounts visible to both partners (with owner tracking)
- **Transactions**: All transactions visible to both partners (with creator tracking)
- **Debts**: All debts visible to both partners (with owner tracking)

### Owner/Creator Tracking
While everything is shared and visible, we track ownership for context:
- **Bank Accounts**: `owner_user_id` shows which partner owns this account
- **Transactions**: `created_by_user_id` shows who entered this transaction
- **Debts**: `owner_user_id` shows whose debt this is

This allows the UI to show "Bob's Chase Checking" or "Transaction by Alice" while still making everything visible to both partners.

## Database Schema Changes

### New Tables

#### 1. `households`
Primary table for household/budget groups.
```sql
CREATE TABLE households (
    id INTEGER PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. `user_household` (Association Table)
Many-to-many relationship between users and households.
```sql
CREATE TABLE user_household (
    user_id INTEGER NOT NULL REFERENCES users(id),
    household_id INTEGER NOT NULL REFERENCES households(id),
    role VARCHAR(20) DEFAULT 'member',  -- 'owner' or 'member'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, household_id)
);
```

#### 3. `household_invites`
Tracks pending invitations to join households.
```sql
CREATE TABLE household_invites (
    id INTEGER PRIMARY KEY,
    household_id INTEGER NOT NULL REFERENCES households(id),
    inviter_id INTEGER NOT NULL REFERENCES users(id),
    invitee_email VARCHAR(120) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, accepted, rejected, expired
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
```

### Modified Tables

#### Updated: `users`
Added default household reference.
```sql
ALTER TABLE users ADD COLUMN default_household_id INTEGER REFERENCES households(id);
```

#### Updated: ALL Tables - Complete Transparency
Changed from `user_id` to `household_id` for complete transparency.
```sql
-- Before
funds.user_id -> users.id
bills.user_id -> users.id
incomes.user_id -> users.id
accounts.user_id -> users.id
transactions.user_id -> users.id
debts.user_id -> users.id

-- After (ALL household-based with owner tracking)
funds.household_id -> households.id
bills.household_id -> households.id
incomes.household_id -> households.id
accounts.household_id -> households.id + owner_user_id -> users.id
transactions.household_id -> households.id + created_by_user_id -> users.id
debts.household_id -> households.id + owner_user_id -> users.id
```

## Migration Strategy

### Backwards Compatibility
The migration automatically creates a default household for each existing user:
1. Create household named "{username}'s Household"
2. Link user as 'owner' role
3. Set as default_household_id
4. Migrate existing funds/bills/incomes to this household

This ensures:
- ✅ Existing single users continue working without changes
- ✅ Zero downtime migration
- ✅ No data loss

### Example Migration Flow
```
Before Migration:
User "john" owns:
  - Funds: Emergency Fund, Vacation Fund
  - Bills: Rent, Electric
  - Accounts: Checking, Savings
  - Transactions: All his purchases

After Migration:
User "john" belongs to "john's Household" (owner)
  Household owns (john sees everything):
    - Funds: Emergency Fund, Vacation Fund
    - Bills: Rent, Electric
    - Accounts: Checking (owner: john), Savings (owner: john)
    - Transactions: All transactions (created_by: john)

When john invites "jane":
  Household "john's Household" members: john (owner), jane (member)
  
  COMPLETE TRANSPARENCY - Both john and jane see:
    - All Funds: Emergency Fund, Vacation Fund
    - All Bills: Rent, Electric
    - All Accounts: john's Checking, john's Savings, jane's Checking
    - All Transactions: john's purchases AND jane's purchases
    - All Debts: john's credit card AND jane's student loan
  
  UI shows ownership: "john's Checking", "Transaction by jane"
  But both partners can see and manage everything!
```

## Model Changes

### household.py (NEW)
```python
class Household(db.Model):
    - id, name, created_by, created_at
    - members (many-to-many via user_household)
    - Methods: add_member(), remove_member(), is_owner()

class HouseholdInvite(db.Model):
    - Invitation tracking with expiration
    - token for secure invite acceptance
```

### user.py (UPDATED)
```python
class User(db.Model):
    + default_household_id (FK to households)
    + households (many-to-many relationship)
    
    to_dict():
        + include_households parameter
        + returns list of households user belongs to
```

### fund.py, bill.py, income.py (UPDATED)
```python
- user_id (REMOVED)
+ household_id (ADDED)
- user relationship (REMOVED)
+ household relationship (ADDED)
```

### account.py (UPDATED - Shared with Owner Tracking)
```python
- user_id (REMOVED)
+ household_id (ADDED - all accounts visible to household)
+ owner_user_id (ADDED - tracks which partner owns this account)
+ household relationship (ADDED)
+ owner relationship (ADDED)
```

### transaction.py (UPDATED - Shared with Creator Tracking)
```python
- user_id (REMOVED)
+ household_id (ADDED - all transactions visible to household)
+ created_by_user_id (ADDED - tracks who created this transaction)
+ household relationship (ADDED)
+ created_by relationship (ADDED)
```

### debt.py (UPDATED - Shared with Owner Tracking)
```python
- user_id (REMOVED)
+ household_id (ADDED - all debts visible to household)
+ owner_user_id (ADDED - tracks whose debt this is)
+ household relationship (ADDED)
+ owner relationship (ADDED)
```

## Next Steps (Not Yet Implemented)

### 1. Authentication & Authorization
- [ ] Update JWT token to include current household_id
- [ ] Create helper decorator `@require_household_access()`
- [ ] Modify routes to check household membership

### 2. API Routes Updates

#### ALL Resources (use household_id - Complete Transparency)
- [ ] `/api/funds/` - Query by household_id
- [ ] `/api/bills/` - Query by household_id  
- [ ] `/api/income/` - Query by household_id
- [ ] `/api/accounts/` - Query by household_id (show owner in UI)
- [ ] `/api/transactions/` - Query by household_id (show creator in UI)
- [ ] `/api/debts/` - Query by household_id (show owner in UI)
- [ ] `/api/dashboard/` - Aggregate by household_id

#### New Routes Needed
- [ ] `POST /api/households/` - Create household
- [ ] `GET /api/households/` - List user's households
- [ ] `GET /api/households/<id>` - Get household details
- [ ] `PUT /api/households/<id>` - Update household
- [ ] `POST /api/households/<id>/invite` - Invite member
- [ ] `POST /api/households/invites/<token>/accept` - Accept invite
- [ ] `DELETE /api/households/<id>/members/<user_id>` - Remove member
- [ ] `POST /api/households/<id>/leave` - Leave household

### 3. Frontend Changes
- [ ] Add household selector/switcher in header
- [ ] Show current household name
- [ ] Create Household Management page
- [ ] Add "Invite Member" flow
- [ ] Update API calls to use household context
- [ ] Show member indicators on shared resources

### 4. User Experience
- [ ] "Switch Household" dropdown (if user belongs to multiple)
- [ ] Household settings page
- [ ] Member management UI
- [ ] Pending invitations list
- [ ] Visual indicators: "Shared with 2 people" badges

## Usage Examples

### Single User (Existing Behavior)
```python
# User creates account
user = User(username='alice', email='alice@example.com')
# Household automatically created: "alice's Household"
# All their funds/bills belong to this household
```

### Couple Sharing Budget (Complete Transparency)
```python
# Alice invites Bob
invite = HouseholdInvite(
    household_id=alice_household.id,
    inviter_id=alice.id,
    invitee_email='bob@example.com'
)

# Bob accepts invitation
alice_household.add_member(bob, role='member')

# Now both Alice and Bob see EVERYTHING:
# - Same Funds: Emergency Fund, Vacation Fund
# - Same Bills: Rent, Electric
# - ALL Accounts: Alice's Checking, Bob's Savings (with owner labels)
# - ALL Transactions: Alice's AND Bob's purchases (with creator labels)
# - ALL Debts: Alice's car loan, Bob's credit card (with owner labels)

# Complete trust and transparency! 🤝
```

### API Query Changes
```python
# OLD: Query by user_id
funds = Fund.query.filter_by(user_id=current_user_id).all()

# NEW: Query by household_id
household_id = get_user_household(current_user_id)
funds = Fund.query.filter_by(household_id=household_id).all()
```

## Testing Checklist (Future)
- [ ] Single user workflow (backwards compatibility)
- [ ] Create household and invite member
- [ ] Accept household invitation
- [ ] Shared fund visible to both members
- [ ] All accounts visible to both members (with owner labels)
- [ ] All transactions visible to both members (with creator labels)
- [ ] Bob creates transaction, Alice sees it immediately
- [ ] Alice adds bank account, Bob sees it in accounts list
- [ ] Transaction updates fund balance for both partners
- [ ] Remove member from household
- [ ] Leave household
- [ ] Delete household (owner only)

## Security Considerations
- Household invites expire after 7 days
- Only household owner can remove members
- Members can leave anytime
- Token-based invite acceptance (secure)
- Email verification recommended before sending invites

## Performance Notes
- user_household association table indexed on both keys
- household_id added to indexes on funds, bills, incomes
- Default household cached in user session/JWT

## File Locations
```
backend/
├── models/
│   ├── household.py (NEW)
│   ├── user.py (UPDATED)
│   ├── fund.py (UPDATED - household_id)
│   ├── bill.py (UPDATED - household_id)
│   ├── income.py (UPDATED - household_id)
│   ├── account.py (unchanged - user_id)
│   ├── transaction.py (unchanged - user_id)
│   └── debt.py (unchanged - user_id)
├── migrations/
│   └── versions/
│       └── household_multiuser_v1.py (NEW)
└── routes/
    └── households_routes.py (TO BE CREATED)
```

## Notes
- Migration is ONE-WAY - downgrade not supported (backup before running)
- Existing users automatically get their own household
- No UI changes required immediately - single users work as before
- Household features can be rolled out gradually
