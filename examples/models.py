from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    created_at: str = "0"
    updated_at: str = "0"
