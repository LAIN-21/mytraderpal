#!/usr/bin/env python3
"""
HTTP Proxy for Lambda RIE
Converts HTTP requests to Lambda invoke format and back
"""
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

LAMBDA_RIE_URL = os.getenv('LAMBDA_RIE_URL', 'http://127.0.0.1:8080')
INVOKE_PATH = '/2015-03-31/functions/function/invocations'


class LambdaProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def _send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-MTP-Dev-User')
        self.send_header('Access-Control-Allow-Credentials', 'true')
    
    def _convert_http_to_lambda_event(self):
        """Convert HTTP request to Lambda event format"""
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)
        
        # Read body if present
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
        
        # Convert headers to dict (normalize keys)
        headers = {}
        for key, value in self.headers.items():
            headers[key.lower()] = value
        
        # Build Lambda event
        event = {
            'httpMethod': self.command,
            'path': path,
            'headers': headers,
            'queryStringParameters': {k: v[0] if len(v) == 1 else v for k, v in query_params.items()} if query_params else None,
            'body': body if body else None,
            'requestContext': {
                'requestId': f'local-{os.urandom(8).hex()}',
                'stage': 'local',
                'httpMethod': self.command,
                'path': path
            }
        }
        
        return event
    
    def _invoke_lambda(self, event):
        """Invoke Lambda via RIE"""
        try:
            response = requests.post(
                f'{LAMBDA_RIE_URL}{INVOKE_PATH}',
                json=event,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error invoking Lambda: {e}", file=sys.stderr)
            return {
                'statusCode': 500,
                'headers': {},
                'body': json.dumps({'error': str(e)})
            }
    
    def _send_lambda_response(self, lambda_response):
        """Convert Lambda response to HTTP response"""
        status_code = lambda_response.get('statusCode', 200)
        headers = lambda_response.get('headers', {})
        body = lambda_response.get('body', '')
        
        self.send_response(status_code)
        
        # Send CORS headers
        self._send_cors_headers()
        
        # Send Lambda response headers
        for key, value in headers.items():
            if key.lower() not in ['access-control-allow-origin', 'access-control-allow-methods', 'access-control-allow-headers']:
                self.send_header(key, value)
        
        self.end_headers()
        self.wfile.write(body.encode('utf-8') if isinstance(body, str) else body)
    
    def do_GET(self):
        """Handle GET requests"""
        event = self._convert_http_to_lambda_event()
        lambda_response = self._invoke_lambda(event)
        self._send_lambda_response(lambda_response)
    
    def do_POST(self):
        """Handle POST requests"""
        event = self._convert_http_to_lambda_event()
        lambda_response = self._invoke_lambda(event)
        self._send_lambda_response(lambda_response)
    
    def do_PUT(self):
        """Handle PUT requests"""
        event = self._convert_http_to_lambda_event()
        lambda_response = self._invoke_lambda(event)
        self._send_lambda_response(lambda_response)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        event = self._convert_http_to_lambda_event()
        lambda_response = self._invoke_lambda(event)
        self._send_lambda_response(lambda_response)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def run(port=9000):
    """Run the HTTP proxy server"""
    server = HTTPServer(('0.0.0.0', port), LambdaProxyHandler)
    print(f"Lambda HTTP Proxy running on port {port}")
    print(f"Proxying to Lambda RIE at {LAMBDA_RIE_URL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down proxy...")
        server.shutdown()


if __name__ == '__main__':
    port = int(os.getenv('PROXY_PORT', '9000'))
    run(port)

