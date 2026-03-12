#!/usr/bin/env python
"""
Test to reproduce the issue where Flask routes command doesn't show subdomain information.

The test creates a Flask app with blueprints registered to different subdomains
and checks if the routes output includes domain/subdomain information.
"""
import sys
from flask import Flask, Blueprint
from flask.cli import FlaskGroup
from click.testing import CliRunner

def test_subdomain_routes():
    """Test that routes command shows subdomain information."""
    # Create Flask app with subdomain matching enabled
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'test.local:5000'

    # Enable subdomain matching (not host matching)
    app.url_map.subdomain_matching = True

    # Create blueprints with different subdomains
    admin_blueprint = Blueprint('admin_blueprint', __name__)
    test_blueprint = Blueprint('test_subdomain_blueprint', __name__)

    @admin_blueprint.route('/home')
    def admin_home():
        return 'Admin Home'

    @test_blueprint.route('/home')
    def test_home():
        return 'Test Home'

    # Register blueprints with subdomains
    app.register_blueprint(admin_blueprint, url_prefix='', subdomain='admin')
    app.register_blueprint(test_blueprint, url_prefix='', subdomain='test')

    # Create CLI runner
    cli = FlaskGroup(create_app=lambda: app)
    runner = CliRunner()

    # Run routes command
    result = runner.invoke(cli, ['routes'])

    print("=== Routes command output ===")
    print(result.output)
    print("=== End of output ===")

    # Check if output contains subdomain information
    # The buggy version should NOT show subdomain information
    # The fixed version SHOULD show subdomain information

    # Check if the output contains subdomain information
    lines = result.output.strip().split('\n')

    # Find the header line
    header_line = lines[0] if lines else ""

    print(f"\nHeader line: '{header_line}'")

    # Check if subdomain information is present in the output
    has_subdomain_column = 'Subdomain' in header_line

    if has_subdomain_column:
        print("\n✓ Test PASSED: Subdomain column is present in routes output")
        print("This indicates the issue is FIXED")
        return True
    else:
        print("\n✗ Test FAILED: Subdomain column is NOT present in routes output")
        print("This indicates the issue is NOT fixed")
        print("Expected to see 'Subdomain' column in the header")
        return False

if __name__ == '__main__':
    success = test_subdomain_routes()
    sys.exit(0 if success else 1)