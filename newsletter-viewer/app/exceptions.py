class NewsletterNotFoundException(Exception):
    def __init__(self, newsletter_id, email, message="Newsletter not found"):
        self.newsletter_id = newsletter_id
        self.email = email
        self.message = f"{message} for ID: {newsletter_id} and email: {email}"
        super().__init__(self.message)

class UnauthorizedAccessException(Exception):
    def __init__(self, message="Unauthorized access to newsletter"):
        self.message = message
        super().__init__(self.message)

class S3AccessException(Exception):
    def __init__(self, message="Error accessing S3 resource"):
        self.message = message
        super().__init__(self.message)
