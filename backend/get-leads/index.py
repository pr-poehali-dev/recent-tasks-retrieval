import os
import json
import psycopg2


def handler(event: dict, context) -> dict:
    """Возвращает список заявок из БД для страницы администратора"""

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Admin-Key',
                'Access-Control-Max-Age': '86400',
            },
            'body': ''
        }

    admin_key = event.get('headers', {}).get('x-admin-key', '')
    if admin_key != os.environ.get('ADMIN_KEY', ''):
        return {
            'statusCode': 401,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': {'error': 'Unauthorized'}
        }

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    try:
        schema = os.environ.get('MAIN_DB_SCHEMA', 'public')
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT id, email, created_at FROM {schema}.leads ORDER BY created_at DESC"
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    leads = [
        {'id': r[0], 'email': r[1], 'created_at': r[2].isoformat()}
        for r in rows
    ]

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': {'leads': leads, 'total': len(leads)}
    }
