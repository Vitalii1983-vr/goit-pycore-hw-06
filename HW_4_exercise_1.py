import sys
from pathlib import Path
from collections import UserDict
import re


# Валідація вводу та обробка помилок


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Не достатньо аргументів. Будь ласка, дотримуйтесь формату команди."
        except ValueError:
            return "Некоректні дані. Переконайтеся, що ви вводите правильні типи даних."
        except KeyError:
            return "Контакт не знайдено."
    return inner


# Базовий клас для полів запису


class Field:
    def __init__(self, value):
        self.value = value  # Ініціалізація значення поля

    def __str__(self):
        return str(self.value)  # Повертає строкове представлення поля


# Клас для зберігання імені контакту


class Name(Field):
    pass  # Наслідування базових властивостей класу Field


# Клас для зберігання номера телефону з валідацією


class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Номер телефону повинен містити рівно 10 цифр.")
        super().__init__(value)  # Виклик конструктора базового класу


# Клас для зберігання інформації про контакт


class Record:
    def __init__(self, name):
        self.name = Name(name)  # Збереження імені як об'єкту класу Name
        self.phones = []  # Ініціалізація списку телефонів

    def add_phone(self, phone):
        self.phones.append(Phone(phone))  # Додавання нового телефону

    def remove_phone(self, phone_number):
        # Видалення телефону
        self.phones = [
            phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_number, new_number):
        found = False
        for phone in self.phones:
            if phone.value == old_number:
                phone.value = new_number  # Оновлення номеру телефону
                found = True
                break
        if not found:
            raise ValueError("Номер телефону не знайдено.")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone  # Пошук телефону за номером
        return None

    def __str__(self):
        return f"Ім'я контакту: {self.name.value}, телефони: {'; '.join(p.value for p in self.phones)}"


# Клас для зберігання та управління записами


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record  # Додавання запису

    def find(self, name):
        return self.data.get(name, None)  # Пошук запису за ім'ям

    def delete(self, name):
        if name in self.data:
            del self.data[name]  # Видалення запису
        else:
            raise KeyError("Запис не знайдено.")


# Функції для обробки команд CLI


def parse_input(user_input):
    cmd, *args = user_input.split()  # Розбір введення на команду та аргументи
    cmd = cmd.strip().lower()  # Нормалізація команди
    return cmd, args


@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise IndexError("Будь ласка, надайте ім'я та хоча б один телефон.")
    name = args[0]
    record = Record(name)
    for phone in args[1:]:
        record.add_phone(phone)
    book.add_record(record)
    return f"Контакт {name} додано з телефонами: {'; '.join(args[1:])}"


@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise IndexError("Введіть ім'я, старий телефон і новий телефон.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Телефон для {name} оновлено з {old_phone} на {new_phone}."
    else:
        raise KeyError(f"Контакт '{name}' не знайдено.")


@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise IndexError("Введіть точно одне ім'я.")
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {'; '.join(phone.value for phone in record.phones)}"
    else:
        raise KeyError(f"Контакт '{name}' не знайдено.")


@input_error
def show_all(book):
    if not book.data:
        return "Контакти відсутні."
    return "\n".join(str(record) for record in book.data.values())


def main():
    book = AddressBook()
    print("Ласкаво просимо до вашого асистента CLI!")

    while True:
        user_input = input("Введіть команду: ")
        command, args = parse_input(user_input)

        command_handlers = {
            'hello': lambda args: "Як я можу вам допомогти?",
            'add': lambda args: add_contact(args, book),
            'change': lambda args: change_contact(args, book),
            'phone': lambda args: show_phone(args, book),
            'all': lambda args: show_all(book),
            'exit': lambda args: "До побачення!",
            'close': lambda args: "До побачення!"
        }

        if command in command_handlers:
            result = command_handlers[command](args)
            print(result)
            if command in ["exit", "close"]:
                break
        else:
            print("Неправильна команда.")


if __name__ == "__main__":
    main()


# Перелік команд, які можна виконувати:


# Цей код підтримує наступні команди для управління адресною книгою через CLI:

# add: Додає новий контакт з ім'ям та одним або кількома телефонами. Наприклад: add Іван 0935673555.
# change: Змінює існуючий телефонний номер на новий для заданого контакту. Наприклад: change Василь 0935673555 0977895555.
# phone: Виводить всі телефонні номери вказаного контакту. Наприклад: phone Василь.
# all: Показує всі контакти та їхні номери, що є в адресній книзі. Наприклад: all.
# exit або close: Завершує роботу програми. Наприклад: exit.
