"""
Test to reproduce the issue where the join filter escapes the joining string
even when autoescape is off.
"""
from django.template import Context, Template
from django.test import TestCase

class JoinAutoescapeTest(TestCase):
    def test_join_with_variable_joiner_and_autoescape_off(self):
        """
        Test that when autoescape is off, the joining string (variable) should NOT be escaped.
        This reproduces the bug described in the issue.
        """
        # Create a template with autoescape off and a variable joiner
        template_str = '{% autoescape off %}{{ some_list|join:some_var }}{% endautoescape %}'

        # Test data
        some_list = ["<p>Hello World!</p>", "beta & me", "<script>Hi!</script>"]
        some_var = "<br/>"

        # Render the template
        template = Template(template_str)
        context = Context({"some_list": some_list, "some_var": some_var})
        output = template.render(context)

        # Expected output: the joiner should NOT be escaped
        expected = "<p>Hello World!</p><br/>beta & me<br/><script>Hi!</script>"

        # This assertion will FAIL on the buggy version because some_var gets escaped to &lt;br/&gt;
        # It will PASS on the fixed version where some_var is not escaped
        self.assertEqual(output, expected,
                        f"Expected: {expected}\nGot: {output}")

if __name__ == "__main__":
    import django
    from django.conf import settings

    # Configure Django settings
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
        }],
    )
    django.setup()

    # Run the test
    test = JoinAutoescapeTest('test_join_with_variable_joiner_and_autoescape_off')
    test._testMethodName = 'test_join_with_variable_joiner_and_autoescape_off'
    test._testMethodDoc = JoinAutoescapeTest.test_join_with_variable_joiner_and_autoescape_off.__doc__
    test.setUp()
    test.test_join_with_variable_joiner_and_autoescape_off()
    print("Test passed - issue is fixed")