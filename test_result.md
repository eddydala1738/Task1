#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Create a Discord bot in Python using discord.py with order management system - users can place orders (product name, quantity), admins can confirm PayPal payments, generate order numbers (ORD-001 format), track order status (Pending->Paid->Processing->Completed), and notify users of status changes"

backend:
  - task: "Discord bot main file with keyword responses and order system"
    implemented: true
    working: "NA"
    file: "discord_bot.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Updated main Discord bot file with order management integration, new keyword responses for orders, and enhanced help system"
  
  - task: "Order management system with database"
    implemented: true
    working: "NA"
    file: "order_manager.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Created comprehensive order management system with SQLite database, order tracking, status updates, and report generation"
  
  - task: "Order commands and user interface"
    implemented: true
    working: "NA"
    file: "order_cogs.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Created order cogs with user commands (/place_order, /my_orders, /order_status) and admin commands (/confirm_payment, /update_order_status, /view_orders, /search_orders, /order_report)"
  
  - task: "Bot configuration with order settings"
    implemented: true
    working: "NA"
    file: "bot_config.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Updated configuration system with order-specific settings, payment methods, and admin role management"
  
  - task: "Bot launcher script"
    implemented: true
    working: true
    file: "run_bot.py"
    stuck_count: 0
    priority: "low"
    needs_retesting: false
    status_history:
        - working: true
          agent: "testing"
          comment: "Previously tested and working - no changes needed"
  
  - task: "Environment configuration with bot token"
    implemented: true
    working: true
    file: ".env"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "testing"
          comment: "Previously tested and working - bot token is properly configured"
  
  - task: "Database dependencies installation"
    implemented: true
    working: "NA"
    file: "requirements.txt"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Added aiosqlite dependency for order database management"

frontend:
  - task: "Not applicable for Discord bot"
    implemented: false
    working: "NA"
    file: "N/A"
    stuck_count: 0
    priority: "low"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Discord bot does not require frontend - it's a standalone Python application"

metadata:
  created_by: "main_agent"
  version: "2.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Order management system with database"
    - "Order commands and user interface"
    - "Discord bot main file with keyword responses and order system"
    - "Bot configuration with order settings"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: "Added comprehensive order management system to Discord bot with: 1) SQLite database for order storage, 2) Complete order lifecycle (Pending->Paid->Processing->Completed), 3) User commands for placing and tracking orders, 4) Admin commands for payment confirmation and order management, 5) Automatic user notifications, 6) Order number generation (ORD-001 format), 7) PayPal payment method support, 8) Search and reporting functionality. Ready for testing to verify database initialization, command functionality, and order processing workflow."