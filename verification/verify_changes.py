from playwright.sync_api import sync_playwright

def verify_changes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 1. Verify Login Page
        print("Checking Login Page...")
        page.goto("http://localhost:8000/authenticate/login/")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="verification/login_page.png")
        print("Login Page Screenshot saved.")

        # Check if flowbite script is present (should NOT be)
        content = page.content()
        if "flowbite.min.js" in content:
            print("ERROR: Flowbite script still present in login page!")
        else:
            print("SUCCESS: Flowbite script removed from login page.")

        # 2. Login
        print("Logging in...")
        # Create a user if needed (we are using existing admin/admin123 from previous steps usually, but let's assume we can login with the one created in docker script or default)
        # Actually I need a valid user. I'll use the one I'm about to create or check if exists.
        # I'll rely on the fact that I can't easily create user from here without django shell.
        # But I can check the layout of login page at least.

        # Taking screenshot of dashboard might require login.
        # I'll skip dashboard verification for now if I don't have credentials,
        # but I can verify the static assets loading.

        # Let's try to login with admin@example.com / admin123 (standard dev credentials)
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin") # Attempt default
        page.click("button[type='submit']")

        # Check if redirected or error
        try:
            page.wait_for_url("**/dashboard/", timeout=5000)
            print("Login successful.")

            # 3. Verify Dashboard Sidebar
            print("Checking Dashboard...")
            page.screenshot(path="verification/dashboard.png")

            # Check Alpine.js sidebar
            # Look for x-data attribute
            if 'x-data="{ sidebarOpen:' in page.content():
                 print("SUCCESS: Alpine.js sidebar detected.")
            else:
                 print("ERROR: Alpine.js sidebar NOT detected.")

        except:
            print("Login failed or not redirected to dashboard. Taking screenshot of error.")
            page.screenshot(path="verification/login_failed.png")

        browser.close()

if __name__ == "__main__":
    verify_changes()
