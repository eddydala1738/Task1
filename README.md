# Discord Bot with Order Management System

A comprehensive Python Discord bot using discord.py 2.5+ with keyword responses, slash commands, and a complete order management system.

## Features

🔧 **Basic Requirements:**
- ✅ Responds to messages with specific keywords (help, rules, join, order, payment, status)
- ✅ Replies support channel mentions using `<#channel_id>`
- ✅ Redirects users to channels when keywords are detected
- ✅ Supports slash commands using discord.app_commands
- ✅ Customizable keyword/command system using configuration files

🛍️ **Order Management System:**
- ✅ Complete order lifecycle (Pending → Paid → Processing → Completed)
- ✅ Order number generation (ORD-001 format)
- ✅ PayPal payment support
- ✅ Admin/moderator payment confirmation
- ✅ Automatic user notifications for status changes
- ✅ Order tracking and history
- ✅ Admin tools for order management and reporting

⚙️ **Technical Details:**
- ✅ Uses discord.py 2.5+ for slash commands
- ✅ SQLite database for order storage
- ✅ Bot token setup via .env file using python-dotenv
- ✅ Comprehensive logging system
- ✅ Modular structure using Cogs
- ✅ Configuration management system

## Available Commands

### 🛍️ User Commands
- `/place_order` - Place a new order (product name + quantity)
- `/my_orders` - View your order history
- `/order_status` - Check status of a specific order

### 📋 General Commands
- `/help` - Shows list of available commands and help info
- `/rules` - Redirects user to the rules channel
- `/join` - Shows instructions on how to join roles or channels
- `/ping` - Confirms the bot is working

### 👑 Admin/Moderator Commands
- `/confirm_payment` - Confirm PayPal payment for an order
- `/update_order_status` - Update order status
- `/view_orders` - View all orders with optional filters
- `/search_orders` - Search orders by order number, username, or product
- `/order_report` - Generate order statistics report

### Keyword Responses
The bot automatically responds to these keywords in messages:
- `help` - Shows available commands
- `rules` - Redirects to rules channel
- `join` - Shows join instructions
- `order` - Information about placing orders
- `payment` - PayPal payment information
- `status` - Order status checking instructions

## Order Management Workflow

1. **User places order**: `/place_order product_name quantity`
   - Order gets unique number (ORD-001, ORD-002, etc.)
   - Status: 🟡 Pending
   - User receives order confirmation

2. **User makes PayPal payment**: User pays via PayPal

3. **Admin confirms payment**: `/confirm_payment ORD-001`
   - Status changes to: 🟢 Paid
   - User gets automatic notification

4. **Admin processes order**: `/update_order_status ORD-001 Processing`
   - Status changes to: 🔄 Processing
   - User gets automatic notification

5. **Admin completes order**: `/update_order_status ORD-001 Completed`
   - Status changes to: ✅ Completed
   - User gets automatic notification

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Bot Token:**
   - The bot token is already set in `backend/.env` file
   - Token: `MTM5MTUwMTQxMzQ2ODg2NDU1Mg.GdiJ6t.iyAtQ68apP5zx6wIi2BadjtpuZpFxJ2ZMfHPDg`

3. **Customize Configuration:**
   - Edit `backend/bot_config.py` to modify responses and channel IDs
   - The bot will create `bot_config.json` for runtime configuration

4. **Run the Bot:**
   ```bash
   cd backend
   python run_bot.py
   ```
   
   Or directly:
   ```bash
   cd backend
   python discord_bot.py
   ```

## File Structure

```
backend/
├── discord_bot.py      # Main bot file with order system integration
├── order_manager.py    # SQLite database operations and order management
├── order_cogs.py       # Order-related Discord commands (user and admin)
├── bot_config.py       # Configuration management with order settings
├── bot_cogs.py         # General command groups (help, rules, join)
├── run_bot.py          # Bot launcher script
├── requirements.txt    # Dependencies (including aiosqlite)
├── orders.db          # SQLite database for orders (auto-created)
└── .env               # Environment variables
```

## Order System Features

### 📊 Order Tracking
- Unique order numbers (ORD-001 format)
- Order status tracking with history
- User and admin order views
- Search functionality

### 🔐 Permission System
- User commands: Anyone can place and track orders
- Admin commands: Restricted to users with "admin", "moderator", or "mod" roles
- Permission validation on all admin functions

### 📈 Reporting
- Order statistics dashboard
- Status breakdown
- Recent order trends
- Export functionality

### 🔔 Notifications
- Automatic user notifications for all status changes
- Rich embed messages with order details
- Direct message notifications to users

## Configuration

### Admin Roles
Configure which roles can manage orders in `bot_config.py`:
```json
"order_settings": {
    "admin_roles": ["admin", "moderator", "mod"]
}
```

### Order Limits
Set order quantity limits:
```json
"settings": {
    "max_order_quantity": 100,
    "min_product_name_length": 2
}
```

### Payment Methods
Configure accepted payment methods:
```json
"order_settings": {
    "payment_methods": ["PayPal"],
    "default_payment_method": "PayPal"
}
```

## Database Schema

The bot automatically creates an SQLite database with these tables:

### Orders Table
- order_number (TEXT, UNIQUE)
- user_id (TEXT)
- username (TEXT)
- product_name (TEXT)
- quantity (INTEGER)
- status (TEXT)
- payment_method (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- confirmed_by (TEXT)
- notes (TEXT)

### Order History Table
- order_number (TEXT)
- status_from (TEXT)
- status_to (TEXT)
- changed_by (TEXT)
- changed_at (TIMESTAMP)
- notes (TEXT)

## Bot Permissions

The bot requires these permissions in your Discord server:
- Read Messages
- Send Messages
- Use Slash Commands
- Embed Links
- Read Message History
- Send Messages in DMs (for notifications)

## Testing the Order System

1. **Start the bot**: `cd backend && python run_bot.py`
2. **Place test order**: `/place_order "Test Product" 2`
3. **Check order status**: `/order_status ORD-001`
4. **Admin confirm payment**: `/confirm_payment ORD-001`
5. **Update order status**: `/update_order_status ORD-001 Processing`
6. **View all orders**: `/view_orders`
7. **Generate report**: `/order_report`

## Troubleshooting

### Common Issues:
1. **Bot not responding**: Check if token is valid and bot is online
2. **Slash commands not working**: Ensure bot has proper permissions
3. **Database errors**: Check file permissions for orders.db
4. **Admin commands not working**: Verify user has correct role

### Order System Issues:
- **Order numbers not generating**: Check database initialization
- **Notifications not sending**: Verify bot can send DMs to users
- **Admin commands restricted**: Ensure user has admin/moderator role

## Next Steps

1. **Add Bot to Server**: Use Discord Developer Portal to add bot to your server
2. **Set Channel IDs**: Replace placeholder IDs with actual channel IDs in config
3. **Configure Admin Roles**: Set up proper admin/moderator roles
4. **Test Order Flow**: Complete end-to-end order testing
5. **Customize Settings**: Adjust order limits and payment methods as needed

The bot is ready to handle both basic Discord bot functionality and complete order management!