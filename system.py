import random
import sqlite3

conn = sqlite3.connect("card.s3db")
cur = conn.cursor()

with conn:
    cur.execute("""CREATE TABLE IF NOT EXISTS card (
                        id INTEGER PRIMARY KEY AUTOINCREMENT ,
                        number TEXT,
                        pin TEXT,
                        balance INTEGER DEFAULT 0)""")


class Atm:

    def __init__(self, iin):
        self.iin = iin  # stands for issuer identification number
        self.checksum = None  # feels like bad practice to include this as its unique when making every card
        self.checked_card = None  # also feels bad
        self.logged_in = False

    # prints out database. Used for testing
    @staticmethod
    def print_database():
        cur.execute("SELECT * FROM card")
        print(cur.fetchall())

    @staticmethod
    def new_row(number, pin):
        with conn:
            cur.execute("INSERT INTO card (number, pin) VALUES (:number, :pin)", {'number': number, 'pin': pin})

    # gets checksum value using luhn algorithm
    def get_checksum(self, pre_checksum):
        digits = dict()
        counter = 1
        sum_digits = 0
        for i in pre_checksum:
            digits[counter] = int(i)
            counter += 1
        for i in digits.keys():
            if i % 2 == 1:
                digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        for i in digits.values():
            sum_digits += i
        mod_10 = sum_digits % 10
        if mod_10 == 0:
            self.checksum = '0'
        else:
            self.checksum = str(10 - mod_10)

    # checks card number using luhn algorithm
    def check_number(self):
        while True:
            check_card = input("Enter your card number:\n")
            pre_checksum = check_card[:-1]
            self.get_checksum(pre_checksum)
            if self.checksum != check_card[-1]:
                print("Probably you made a mistake in the card number. Please try again!\n")
                continue
            else:
                self.checked_card = check_card
                break

    def create_account(self):
        identifier = f'{random.randrange(1, 10 ** 9):09}'
        pre_checksum = self.iin + identifier
        self.get_checksum(pre_checksum)
        card_number = pre_checksum + self.checksum
        pin = f'{random.randrange(1, 10 ** 4):04}'
        self.new_row(card_number, pin)
        print("\nYour card has been created")
        print(f"Your card number:\n{card_number}")
        print(f"Your card PIN:\n{pin}\n")

    def log_in(self):
        self.check_number()
        check_card = self.checked_card
        check_pin = input("Enter your PIN:\n")
        cur.execute("SELECT pin FROM card WHERE number=:number", {'number': check_card})
        correct_pin = cur.fetchone()
        if correct_pin is not None:
            if check_pin == correct_pin[0]:
                print("\nYou have successfully logged in!\n")
                self.logged_in = True
            else:
                print("Wrong card number or PIN!\n")
        else:
            print("Wrong card number or PIN!\n")
        while self.logged_in is True:
            self.actions_logged_in(check_card)

    @staticmethod
    def check_balance(number):
        cur.execute("SELECT balance FROM card WHERE number=:number", {'number': number})
        balance = cur.fetchone()[0]
        print(f"Balance: {balance}\n")

    @staticmethod
    def add_income(number):
        cur.execute("SELECT balance FROM card WHERE number=:number", {'number': number})
        balance = cur.fetchone()[0]
        income = int(input("Enter income:\n"))
        balance += income
        with conn:
            cur.execute("UPDATE card SET balance = :balance WHERE number=:number", {'balance': balance, 'number': number})
        print("Income was added!\n")

    # coding this will be fun
    # update: it works but this is a mess
    # perhaps can be broken into check card and transfer
    def transfer(self, number):
        self.check_number()
        t_number = self.checked_card
        if number == t_number:
            print("You can't transfer money to the same account!\n")
        else:
            cur.execute("SELECT number FROM card WHERE number=:number", {'number': t_number})
            t_number = cur.fetchone()
            if t_number is None:
                print("Such a card does not exist.\n")
            else:
                cur.execute("SELECT balance FROM card WHERE number=:number", {'number': number})
                balance = cur.fetchone()[0]
                money_to_transfer = int(input("Enter how much money you want to transfer:\n"))
                if money_to_transfer > balance:
                    print("Not enough money!\n")
                else:
                    t_number = t_number[0]
                    balance -= money_to_transfer
                    cur.execute("SELECT balance FROM card WHERE number=:number", {'number': t_number})
                    t_balance = cur.fetchone()[0]
                    t_balance += money_to_transfer
                    with conn:
                        cur.execute("UPDATE card SET balance = :balance WHERE number=:number",
                                    {'balance': balance, 'number': number})
                        cur.execute("UPDATE card SET balance = :balance WHERE number=:number",
                                    {'balance': t_balance, 'number': t_number})
                    print("Success!\n")

    @staticmethod
    def close_account(number):
        with conn:
            cur.execute("DELETE FROM card WHERE number=:number", {'number': number})

    def actions_logged_in(self, number):
        while True:
            print("1. Balance\n2. Add income\n3. Do transfer (WIP)\n4. Close account\n5. Log out\n0. Exit")
            u_action = input()
            if u_action == "1":
                self.check_balance(number)
                continue
            elif u_action == "2":
                self.add_income(number)
                continue
            elif u_action == "3":
                self.transfer(number)
                continue
            elif u_action == "4":
                self.close_account(number)
                print("The account has been closed!\n")
                self.logged_in = False
                break
            elif u_action == "5":
                self.logged_in = False
                print()
                break
            elif u_action == "0":
                exit()
            else:
                print("Sorry, I did not understand that\n")
                continue

    def main(self):
        while True:
            print("1. Create an account\n2. Log into account\n0. Exit")
            u_action = input()
            if u_action == "1":
                self.create_account()
                continue
            elif u_action == "2":
                self.log_in()
            elif u_action == "0":
                print("\nBye!")
                break
            else:
                print("Sorry, I did not understand that\n")
                continue


your_atm = Atm('400000')
your_atm.main()

# code works pretty good but it's a mess
