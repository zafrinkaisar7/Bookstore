from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from books.models import Book
import time


class SeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Use Firefox WebDriver
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")  # Run in headless mode
        cls.selenium = webdriver.Firefox(options=options)
        cls.selenium.implicitly_wait(10)

        # Create test user
        cls.test_user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        # Create test book
        cls.test_book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            description="Test Description",
            price=9.99,
            stock=10,
        )

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Ensure we're logged out before each test
        self.selenium.get(f"{self.live_server_url}/accounts/logout/")
        time.sleep(1)  # Give time for logout to complete

    def test_home_page(self):
        """Test that the home page loads correctly"""
        self.selenium.get(self.live_server_url)
        self.assertIn("BookStore", self.selenium.title)

    def test_login_button(self):
        """Test that the Login button redirects to the login page"""
        self.selenium.get(self.live_server_url)
        login_button = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Login"))
        )
        login_button.click()
        self.assertIn("/login/", self.selenium.current_url)

    def test_explore_books_button(self):
        """Test that the Explore Books button redirects to the books page"""
        self.selenium.get(self.live_server_url)
        explore_button = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Explore Books"))
        )
        explore_button.click()
        self.assertIn("/books/", self.selenium.current_url)

    def test_search_button(self):
        """Test the search button in the navbar (requires login)"""
        # First login
        self.selenium.get(f"{self.live_server_url}/login/")
        username_input = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys("testuser")
        password_input.send_keys("testpass123")
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Now test search
        search_input = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_input.send_keys("Test Book")
        search_input.submit()
        self.assertIn("Test Book", self.selenium.page_source)

    def test_logout_button(self):
        """Test the logout button works"""
        # First login
        self.selenium.get(f"{self.live_server_url}/login/")
        username_input = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys("testuser")
        password_input.send_keys("testpass123")
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Now test logout
        try:
            logout_link = WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
            )
            logout_link.click()
            self.assertIn("/login/", self.selenium.current_url)
        except Exception as e:
            print(f"Error during logout button test: {str(e)}")
            raise

    def test_signup_flow(self):
        """Test the signup flow works"""
        self.selenium.get(f"{self.live_server_url}/signup/")
        username_input = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        email_input = self.selenium.find_element(By.NAME, "email")
        password1_input = self.selenium.find_element(By.NAME, "password1")
        password2_input = self.selenium.find_element(By.NAME, "password2")

        username_input.send_keys("newuser")
        email_input.send_keys("newuser@example.com")
        password1_input.send_keys("newpass123")
        password2_input.send_keys("newpass123")

        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.assertIn("/login/", self.selenium.current_url)
