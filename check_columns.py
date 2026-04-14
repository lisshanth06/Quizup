import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'quiz_app_csi.settings'
django.setup()

from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='quizzes_participant'")
columns = [r[0] for r in cursor.fetchall()]
print("Columns:", columns)

if 'verified' in columns:
    print(">>> 'verified' column STILL EXISTS. Dropping it now...")
    cursor.execute("ALTER TABLE quizzes_participant DROP COLUMN verified")
    print(">>> DONE. Column dropped.")
else:
    print(">>> 'verified' column does NOT exist. All good.")
