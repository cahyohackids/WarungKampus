from collections import deque

# OOP 1: Basic OOP
class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

    def display(self):
        print(f"Book: {self.title} by {self.author} ({self.year})")

# OOP 2: Advanced OOP (Inheritance & Polymorphism)
class Ebook(Book):
    def __init__(self, title, author, year, file_size):
        super().__init__(title, author, year)
        self.file_size = file_size

    def display(self):
        print(f"Ebook: {self.title} by {self.author} ({self.year}) - File Size: {self.file_size}MB")

# Stack and Queue
class LibraryManager:
    def __init__(self):
        self.book_list = []        # List of books
        self.borrow_history = []   # Stack for borrow history
        self.borrow_queue = deque()  # Queue for borrow requests

    def add_book(self, book):
        self.book_list.append(book)
        print(f"Book '{book.title}' added to library.")

    def borrow_book(self, title):
        for book in self.book_list:
            if book.title == title:
                self.book_list.remove(book)
                self.borrow_history.append(book)
                self.borrow_queue.append(book)
                print(f"Book '{title}' borrowed.")
                return
        print(f"Book '{title}' not found.")

    def return_book(self):
        if self.borrow_queue:
            returned_book = self.borrow_queue.popleft()
            self.book_list.append(returned_book)
            print(f"Book '{returned_book.title}' returned.")
        else:
            print("No books to return.")

    def undo_borrow(self):
        if self.borrow_history:
            last_borrowed = self.borrow_history.pop()
            self.book_list.append(last_borrowed)
            self.borrow_queue.remove(last_borrowed)
            print(f"Undo borrow: Book '{last_borrowed.title}' returned to library.")
        else:
            print("No borrow actions to undo.")

    def show_books(self):
        if self.book_list:
            print("Available Books:")
            for book in self.book_list:
                book.display()
        else:
            print("No books available.")

# POP: Procedural Function to Run the Library Manager
def run_library_manager():
    manager = LibraryManager()

    while True:
        print("\nOptions:")
        print("1. Add Book")
        print("2. Add Ebook")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. Undo Borrow")
        print("6. Show Books")
        print("7. Exit")

        choice = input("Choose an option (1-7): ")

        if choice == "1":
            title = input("Enter book title: ")
            author = input("Enter author: ")
            year = input("Enter publication year: ")
            book = Book(title, author, year)
            manager.add_book(book)

        elif choice == "2":
            title = input("Enter ebook title: ")
            author = input("Enter author: ")
            year = input("Enter publication year: ")
            file_size = input("Enter file size (MB): ")
            ebook = Ebook(title, author, year, file_size)
            manager.add_book(ebook)

        elif choice == "3":
            title = input("Enter the title of the book to borrow: ")
            manager.borrow_book(title)

        elif choice == "4":
            manager.return_book()

        elif choice == "5":
            manager.undo_borrow()

        elif choice == "6":
            manager.show_books()

        elif choice == "7":
            print("Exiting Library Manager.")
            break

        else:
            print("Invalid option. Please try again.")

# Main Execution
if __name__ == "__main__":
    run_library_manager()
