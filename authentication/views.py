from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from django.db import connections
import json
import pyodbc
from messaging.utils import is_it_member_user

User = get_user_model()
IT_MEMBER_USERNAMES = ['s20330', '250479', '230022', '140287', '111075', 'ithelpdesk']

@csrf_exempt
@require_http_methods(["POST"])
def ldap_login(request):
    """Login view using standard Django authentication."""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)
        
        # Use Django's standard authentication
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            user.status = 'online'
            user.save()
            
            # Add user to all groups automatically
            from messaging.models import Conversation
            from django.contrib.auth.models import Group as AuthGroup
            
            try:
                # Only predefined IT users should be treated as IT members.
                if user.username in IT_MEMBER_USERNAMES:
                    gti_group = AuthGroup.objects.get(name='GTI members')
                    if not gti_group.user_set.filter(id=user.id).exists():
                        gti_group.user_set.add(user)

                    it_helpdesk_group = AuthGroup.objects.filter(name__iexact='IT help desk').first()
                    if it_helpdesk_group and not it_helpdesk_group.user_set.filter(id=user.id).exists():
                        it_helpdesk_group.user_set.add(user)
            except AuthGroup.DoesNotExist:
                print(f"ERROR: IT groups not found for user {user.username}")
            
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.get_full_name(),
                    'profile_picture': user.profile_picture.url if user.profile_picture else None,
                    'status': user.status,
                    'status_message': user.status_message,
                    'is_it_member': is_it_member_user(user),
                }
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    """Signup view for creating new users."""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        full_name = data.get('full_name', '').strip()
        department = data.get('department', '')
        section = data.get('section', '')

        if full_name and not first_name and not last_name:
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            department=department,
            section=section,
            is_ldap_user=False
        )
        
        # New signups remain normal users by default.
        from messaging.models import Conversation
        
        # Create individual chats with configured IT members.
        it_members = User.objects.filter(username__in=IT_MEMBER_USERNAMES)
        
        for it_member in it_members:
            # Check if individual chat already exists
            existing_chat = Conversation.objects.filter(
                conversation_type='individual'
            ).filter(participants=user).filter(participants=it_member).first()
            
            if not existing_chat:
                # Create individual chat
                chat = Conversation.objects.create(conversation_type='individual')
                chat.participants.add(user, it_member)

        # Ensure the user can see the IT Help Desk group conversation.
        helpdesk_conv = Conversation.objects.filter(
            conversation_type='group',
            group__name__iexact='IT help desk'
        ).first()
        if helpdesk_conv:
            helpdesk_conv.participants.add(user)
        
        # Auto-login after signup
        login(request, user)
        user.status = 'online'
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Signup successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'status': user.status,
                'is_it_member': is_it_member_user(user),
            }
        })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def user_profile(request):
    """Get current user profile."""
    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name(),
        'profile_picture': user.profile_picture.url if user.profile_picture else None,
        'status': user.status,
        'status_message': user.status_message,
        'last_seen': user.last_seen.isoformat(),
        'is_it_member': is_it_member_user(user),
    })


@login_required
def all_users(request):
    """Get all users for chat selection."""
    search = request.GET.get('search', '')
    users = User.objects.all()
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    users_data = [
        {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'status': user.status,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
        }
        for user in users.exclude(id=request.user.id)
    ]
    return JsonResponse({'users': users_data})


@login_required
@require_http_methods(["POST"])
def update_status(request):
    """Update user status."""
    try:
        data = json.loads(request.body)
        status = data.get('status')
        status_message = data.get('status_message', '')
        
        if status in ['online', 'offline', 'away', 'busy']:
            request.user.status = status
            request.user.status_message = status_message
            request.user.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid status'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def logout_view(request):
    """Logout view."""
    request.user.status = 'offline'
    request.user.save()
    logout(request)
    return JsonResponse({'success': True})


@login_required
def update_profile(request):
    """Update user profile."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'status_message' in data:
                user.status_message = data['status_message']
            
            user.save()
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def change_password(request):
    """Change the current user's password."""
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            return JsonResponse({'error': 'All password fields are required.'}, status=400)

        if new_password != confirm_password:
            return JsonResponse({'error': 'New passwords do not match.'}, status=400)

        user = request.user
        if not user.check_password(current_password):
            return JsonResponse({'error': 'Current password is incorrect.'}, status=400)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)

        return JsonResponse({'success': True, 'message': 'Password changed successfully.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def fetch_employee_details(request):
    """Fetch employee details from SQL Server based on employee code."""
    try:
        emp_code = request.GET.get('emp_code')
        
        if not emp_code:
            return JsonResponse({'error': 'Employee code is required'}, status=400)

        employee_data = get_employee_data_from_mssql(emp_code)

        if not employee_data:
            return JsonResponse({'error': 'Employee not found or inactive'}, status=404)

        return JsonResponse({
            'success': True,
            'emp_code': employee_data['emp_code'],
            'emp_name': employee_data['full_name'],
            'department': employee_data['department'],
            'section': employee_data['section'],
            'gti_email': employee_data['email'],
            'source_database': employee_data.get('source_database', '')
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({'error': f'{str(e)} - {traceback.format_exc()}'}, status=500)


def get_employee_data_from_mssql(username):
    """Fetch employee data from Payroll, PayrollITI, and PayTemp using direct pyodbc."""
    server = '10.40.10.105'
    databases = ['Payroll', 'PayrollITI', 'PayTemp']
    username_db = 'paydev'
    password = 'dev.gtipay@123'
    driver = 'ODBC Driver 17 for SQL Server'

    for database in databases:
        conn = None
        cursor = None
        try:
            print(f"DEBUG: Checking employee {username} in {database} database")
            conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username_db};PWD={password}'
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            query = f"""
            select a.empcode,a.empname,b.deptname,c.nsection 
            from [{database}].dbo.empmast as a 
            left join [{database}].dbo.deptmast as b on b.deptcode=a.deptcode 
            left join [{database}].dbo.nsecmast as c on c.nseccode=a.nseccode 
            where a.active='Y' and upper(a.empcode) = upper(?)
            """
            cursor.execute(query, [username])
            result = cursor.fetchone()

            if result:
                print(f"DEBUG: Employee {username} found in {database} database")
                return {
                    'emp_code': result[0] if result[0] else '',
                    'full_name': result[1] if result[1] else '',
                    'department': result[2] if result[2] else '',
                    'section': result[3] if result[3] else '',
                    'email': f"{result[0]}@gti.nws.cn" if result[0] else '',
                    'source_database': database
                }
            print(f"DEBUG: Employee {username} not found in {database} database")
        except pyodbc.Error as e:
            error_code = e.args[0] if getattr(e, 'args', None) else 'unknown'
            print(f"WARNING: {database} database lookup failed for {username} ({error_code})")
        except Exception as e:
            print(f"WARNING: Employee lookup failed in {database} for {username}: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return None


@csrf_exempt
@require_http_methods(["GET"])
def test_database_connection(request):
    """Test database connection and basic query"""
    try:
        print("DEBUG: Testing database connection using pyodbc")
        
        # First check if pyodbc is available
        print(f"DEBUG: pyodbc version: {pyodbc.version}")
        
        # Check available ODBC drivers
        drivers = pyodbc.drivers()
        print(f"DEBUG: Available ODBC drivers: {drivers}")
        
        # Database connection parameters
        server = '10.40.10.105'
        database = 'Payroll'
        username_db = 'paydev'
        password = 'dev.gtipay@123'
        driver = 'ODBC Driver 17 for SQL Server'
        
        # Check if the required driver is available
        if driver not in drivers:
            print(f"DEBUG: Required driver '{driver}' not found in available drivers")
            return JsonResponse({
                'success': False,
                'error': f"Required driver '{driver}' not found. Available drivers: {drivers}",
                'message': 'ODBC driver not available'
            })
        
        # Create connection string
        conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username_db};PWD={password}'
        
        print(f"DEBUG: Connection string: DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username_db};PWD=***")
        
        # Connect to database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("DEBUG: Connected to SQL Server successfully")
        
        # Test basic query to see if we can connect
        test_query = "SELECT COUNT(*) FROM empmast"
        cursor.execute(test_query)
        count = cursor.fetchone()[0]
        print(f"DEBUG: Total employees in empmast: {count}")
        
        # Test if the specific employee exists
        emp_query = "SELECT TOP 5 empcode, empname FROM empmast WHERE empcode LIKE '111075%'"
        cursor.execute(emp_query)
        results = cursor.fetchall()
        print(f"DEBUG: Employees matching 111075: {results}")
        
        # Test the exact query with employee ID
        exact_query = "SELECT a.empcode, a.empname, b.deptname, c.nsection FROM empmast a LEFT JOIN deptmast b ON b.deptcode = a.deptcode LEFT JOIN nsecmast c ON c.nseccode = a.nseccode WHERE a.active = 'Y' AND a.empcode = ?"
        cursor.execute(exact_query, ['111075'])
        exact_result = cursor.fetchone()
        print(f"DEBUG: Exact query result for 111075: {exact_result}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return JsonResponse({
            'success': True,
            'total_employees': count,
            'matching_employees': results,
            'exact_result': exact_result,
            'available_drivers': drivers,
            'message': 'Database connection successful'
        })
        
    except Exception as e:
        print(f"DEBUG: Database connection error: {str(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Database connection failed'
        })

@csrf_exempt
@require_http_methods(["GET"])
def test_database_tables(request):
    """Test if EMPMAST, DEPTMAST, NSECMAST tables exist in PayrollIT database"""
    try:
        print("DEBUG: Testing database tables using pyodbc")
        
        # Database connection parameters
        server = '10.40.10.105'
        database = 'PayrollIT'
        username_db = 'paydev'
        password = 'dev.gtipay@123'
        driver = 'ODBC Driver 17 for SQL Server'
        
        # Create connection string
        conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username_db};PWD={password}'
        
        print(f"DEBUG: Connection string: DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username_db};PWD=***")
        
        # Connect to database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("DEBUG: Connected to SQL Server successfully")
        
        # Test if tables exist
        tables = ['EMPMAST', 'DEPTMAST', 'NSECMAST']
        existing_tables = []
        for table in tables:
            query = f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table}'"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            if count > 0:
                existing_tables.append(table)
        
        # Close connection
        cursor.close()
        conn.close()
        
        return JsonResponse({
            'success': True,
            'existing_tables': existing_tables,
            'message': 'Database tables checked successfully'
        })
        
    except Exception as e:
        print(f"DEBUG: Database connection error: {str(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Database connection failed'
        })

@csrf_exempt
@require_http_methods(["GET"])
def test_mock_data(request):
    """Test mock data for auto-fetch functionality"""
    username = request.GET.get('username', '').strip()
    print(f"DEBUG: Mock test called with username: {username}")
    
    # Mock employee data for testing
    mock_employees = {
        '111075': {
            'emp_code': '111075',
            'full_name': 'John Doe',
            'department': 'IT',
            'section': 'Development',
            'email': '111075@gti.nws.cn'
        },
        '250479': {
            'emp_code': '250479',
            'full_name': 'Jane Smith',
            'department': 'HR',
            'section': 'Recruitment',
            'email': '250479@gti.nws.cn'
        }
    }
    
    if username in mock_employees:
        employee_data = mock_employees[username]
        print(f"DEBUG: Mock data found for {username}: {employee_data}")
        return JsonResponse({
            'success': True,
            'employee_data': employee_data,
            'message': 'Mock data returned successfully'
        })
    else:
        print(f"DEBUG: No mock data found for {username}")
        return JsonResponse({
            'success': False,
            'error': 'Employee not found in mock data',
            'message': 'Mock employee not found'
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_employee_details(request):
    """AJAX endpoint to fetch employee details from paydev database"""
    username = request.GET.get('username', '').strip()
    print(f"DEBUG: get_employee_details called with username: {username}")
    
    if not username:
        return JsonResponse({'error': 'Username is required'})
    
    # Get real employee data from paydev database
    employee_data = get_employee_data_from_mssql(username)
    
    if employee_data:
        print(f"DEBUG: Employee found in database: {employee_data}")
        return JsonResponse({'success': True, 'employee_data': employee_data})
    else:
        print(f"DEBUG: Employee {username} not found in paydev database")
        return JsonResponse({'success': False, 'error': 'Employee not found'})
