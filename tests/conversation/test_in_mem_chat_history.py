import threading
import unittest

from genia.conversation.llm_conversation_in_memory_repository import (
    ThreadSafeDictionary,
)


class ThreadSafeDictionaryTests(unittest.TestCase):
    def test_getitem(self):
        dictionary = ThreadSafeDictionary()
        dictionary["key"] = "value"
        self.assertEqual(dictionary["key"], "value")

    def test_setitem(self):
        dictionary = ThreadSafeDictionary()
        dictionary["key"] = "value"
        self.assertIn("key", dictionary)
        self.assertEqual(dictionary["key"], "value")

    def test_delitem(self):
        dictionary = ThreadSafeDictionary()
        dictionary["key"] = "value"
        del dictionary["key"]
        self.assertNotIn("key", dictionary)

    def test_len(self):
        dictionary = ThreadSafeDictionary()
        dictionary["key1"] = "value1"
        dictionary["key2"] = "value2"
        self.assertEqual(len(dictionary), 2)

    def test_contains(self):
        dictionary = ThreadSafeDictionary()
        dictionary["key"] = "value"
        self.assertIn("key", dictionary)
        self.assertNotIn("nonexistent_key", dictionary)

    def test_get(self):
        dictionary = ThreadSafeDictionary()
        dictionary["key"] = "value"
        self.assertEqual(dictionary.get("key"), "value")
        self.assertEqual(dictionary.get("nonexistent_key", "default"), "default")

    def test_keys(self):
        dictionary = ThreadSafeDictionary()
        dictionary["key1"] = "value1"
        dictionary["key2"] = "value2"
        self.assertCountEqual(dictionary.keys(), ["key1", "key2"])

    def test_values(self):
        dictionary = ThreadSafeDictionary()
        dictionary["key1"] = "value1"
        dictionary["key2"] = "value2"
        self.assertCountEqual(dictionary.values(), ["value1", "value2"])

    def test_items(self):
        dictionary = ThreadSafeDictionary()
        dictionary["key1"] = "value1"
        dictionary["key2"] = "value2"
        self.assertCountEqual(dictionary.items(), [("key1", "value1"), ("key2", "value2")])

    def test_thread_safety(self):
        # Create a ThreadSafeDictionary instance
        dictionary = ThreadSafeDictionary()

        # Define a shared variable to track modifications
        shared_variable = {"count": 0}

        # Define a function that increments the shared variable
        def increment_shared_variable():
            for _ in range(10000):
                with dictionary._lock:
                    shared_variable["count"] += 1

        # Create two threads to increment the shared variable simultaneously
        thread1 = threading.Thread(target=increment_shared_variable)
        thread2 = threading.Thread(target=increment_shared_variable)

        # Start the threads
        thread1.start()
        thread2.start()

        # Wait for the threads to complete
        thread1.join()
        thread2.join()

        # Assert that the shared variable has been incremented correctly
        expected_count = 10000 * 2  # Each thread increments 10000 times
        self.assertEqual(shared_variable["count"], expected_count)


if __name__ == "__main__":
    unittest.main()
