import unittest
import time
from app import app
from database import init_db, get_db_connection

class TruthLensAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret'
        self.client = app.test_client()
        init_db()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TruthLens', response.data)

    def test_full_user_flow(self):
        unique_email = f"unittest_{int(time.time()*1000)}@truthlens.ai"

        # 1. Register User
        reg_res = self.client.post('/register', data={
            'name': 'Test User',
            'email': unique_email,
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(reg_res.status_code, 200)
        self.assertIn(b'Welcome back', reg_res.data)

        # 2. Test Prediction Route
        pred_res = self.client.post('/predict', data={
            'news_text': "SHOCKING SECRET: Scientists Discover Miracle Herb That Instantly Cures All Diseases Overnight! You won't believe what Big Pharma has been hiding from you!"
        }, follow_redirects=True)
        self.assertEqual(pred_res.status_code, 200)
        self.assertIn(b'NEWS FORENSICS REPORT', pred_res.data)
        self.assertIn(b'POSSIBLY FAKE', pred_res.data)
        self.assertIn(b'Clickbait Detector', pred_res.data)

        # 3. Test History Route
        hist_res = self.client.get('/history')
        self.assertEqual(hist_res.status_code, 200)
        self.assertIn(b'SHOCKING SECRET', hist_res.data)

        # 4. Test Report Detail Route (Get the saved prediction ID)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM predictions ORDER BY id DESC LIMIT 1")
        pred_id = cursor.fetchone()['id']
        conn.close()

        report_res = self.client.get(f'/report/{pred_id}')
        self.assertEqual(report_res.status_code, 200)
        self.assertIn(b'NEWS FORENSICS REPORT', report_res.data)

        # 5. Test Model Performance Route
        perf_res = self.client.get('/model-performance')
        self.assertEqual(perf_res.status_code, 200)
        self.assertIn(b'Accuracy', perf_res.data)

        # 6. Test About Route
        about_res = self.client.get('/about')
        self.assertEqual(about_res.status_code, 200)
        self.assertIn(b'Project Objective', about_res.data)

        print("[SUCCESS] All automated route and model pipeline tests passed cleanly!")

if __name__ == '__main__':
    unittest.main()
