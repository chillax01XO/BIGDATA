import datetime

class Homework:
    def __init__(self, text: str, days_to_complete: int):

        self.text = text
        self.deadline = datetime.timedelta(days=days_to_complete)
        self.created = datetime.datetime.now()

    def is_active(self) -> bool:
        return datetime.datetime.now() < self.created + self.deadline


class Student:
    def __init__(self, first_name: str, last_name: str):

        self.first_name = first_name
        self.last_name = last_name

    def do_homework(self, homework: Homework):
        if homework.is_active():
            return homework
        print("You are late")
        return None


class Teacher:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    @staticmethod
    def create_homework(text: str, days_to_complete: int) -> Homework:
        return Homework(text, days_to_complete)


if __name__ == "__main__":
    teacher = Teacher("Daniil", "Shadrin")
    student = Student("Roman", "Petrov")

    print(teacher.first_name)  # Daniil
    print(student.last_name)  # Petrov

    expired_homework = teacher.create_homework("Learn functions", 0)
    print(expired_homework.created)
    print(expired_homework.deadline)  # 0:00:00
    print(expired_homework.text)  # 'Learn functions'

    create_homework_too = teacher.create_homework
    oop_homework = create_homework_too("Create 2 simple classes", 5)
    print(oop_homework.deadline)  # 5 days, 0:00:00

    student.do_homework(oop_homework)
    student.do_homework(expired_homework)  # You are late