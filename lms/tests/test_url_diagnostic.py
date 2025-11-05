from django.test import TestCase
from django.urls import reverse, get_resolver


class URLDiagnosticTest(TestCase):
    """Diagnostic test to find available URL names"""

    def test_list_all_urls(self):
        """List all available URL patterns"""
        resolver = get_resolver()
        url_patterns = []

        def list_urls(patterns, namespace=None, prefix=''):
            for pattern in patterns:
                if hasattr(pattern, 'url_patterns'):
                    # This is an include
                    new_namespace = pattern.namespace
                    if namespace and new_namespace:
                        new_namespace = f"{namespace}:{new_namespace}"
                    elif new_namespace:
                        new_namespace = new_namespace
                    else:
                        new_namespace = namespace

                    list_urls(pattern.url_patterns, new_namespace, prefix + str(pattern.pattern))
                else:
                    # This is a URL pattern
                    if hasattr(pattern, 'name') and pattern.name:
                        full_name = f"{namespace}:{pattern.name}" if namespace else pattern.name
                        url_patterns.append({
                            'name': full_name,
                            'pattern': prefix + str(pattern.pattern),
                            'namespace': namespace,
                            'view_name': pattern.name
                        })

        list_urls(resolver.url_patterns)

        print("\n=== AVAILABLE URL PATTERNS ===")
        for url in sorted(url_patterns, key=lambda x: x['name']):
            print(f"Name: {url['name']}")
            print(f"Pattern: {url['pattern']}")
            print("---")

        # Check for course-related URLs
        course_urls = [url for url in url_patterns if 'course' in url['name'].lower()]
        print("\n=== COURSE-RELATED URLS ===")
        for url in course_urls:
            print(f"Name: {url['name']}")
            print(f"Pattern: {url['pattern']}")
            print("---")

    def test_find_course_create_url(self):
        """Try to find the course creation URL"""
        # Common course creation URL names
        possible_names = [
            'course-create',
            'course_create',
            'create_course',
            'course-create-view',
            'lms:course-create',
            'courses:create',
            'course_new',
            'course-add',
        ]

        print("\n=== TESTING COURSE CREATE URL NAMES ===")
        for name in possible_names:
            try:
                url = reverse(name)
                print(f"✓ FOUND: {name} -> {url}")
            except Exception as e:
                print(f"✗ {name}: {e}")