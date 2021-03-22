from sqlite3 import Error
import sqlite3


class EZBank:

    def __init__(self):

        self.database_file = 'card.s3db'
        self.conn = sqlite3.connect(self.database_file)
        self.INN = '400000'
        self.card = ''

        # instead of dictionary, I need a database connection to a db sqlite db file
        # named card.s3db

        self.user = []

        self.card_list = []
        self.logged_on = False
        self.balance = 0

        self.setup_database(self.database_file)

    def start_menu(self):
        choice = 3

        while choice != 0:
            if self.logged_on:
                print('''
                1. Balance
                2. Add income
                3. Do transfer
                4. Close account
                5. Log out
                0. Exit  ''')
                try:
                    choice = int(input())
                except KeyError:
                    print('Not a supported Option')

                if choice == 1:
                    print(f'Balance: {self.get_balance(self.user[0])}')

                elif choice == 2:
                    income = self.deposit_prompt()
                    if income > 0:
                        self.deposit_in_account(self.user[0], income)
                elif choice == 3:
                    try:
                        print('Transfer')
                        print('Enter card number:')
                        transfer_card = input()
                        if self.verify_transfer(self.user[0], transfer_card):
                            print('Enter how much money you want to transfer:')
                            transfer_amount = int(input())
                            self.transfer_to_account(self.user[0], transfer_card, transfer_amount)
                    except KeyError:
                        print('Please enter a number!')


                elif choice == 4:
                    self.close_account(self.user[0], self.user[1])
                    self.logged_on = False

                elif choice == 5:
                    self.logged_on = False
            else:

                print('''
                1. Create an account
                2. Log into account
                0. Exit  ''')

                try:
                    choice = int(input())
                except KeyError:
                    print('Not a supported Option')

                if choice == 1:
                    self.create_account()

                elif choice == 2:
                    self.login()

            # if database is open still, close it.
            if self.conn:
                self.conn.close()

    def deposit_prompt(self):
        income = 0
        try:
            print('Enter income:')
            return int(input())
        except KeyError:
            print('Please enter a number!')
            return 0

    def get_balance(self, card):
        conn = sqlite3.connect(self.database_file) # replace with self.database_file
        current_balance = 0
        try:
            cur = conn.cursor()
            sql = f"""
            SELECT *
            FROM card
            WHERE number = '{card}'
            """

            cur.execute(sql)
            current_balance = cur.fetchone()[3]
            conn.commit()
            return current_balance


        except Error as e:
            print(e)

        finally:
            conn.close()

    def create_account(self):
        """
        will generate a new card that passes luhn's altorithm
        and generate a 4 digit pin.  Then add them to the database file
        """
        import random
        new_card = ''
        new_pin = ''

        # set the pin#
        new_pin = ('0000' + str(random.randint(0, 9999)))[-4:]

        # find a unique card#
        while(True):
            new_card = '400000' + str(random.randint(1000000000, 9999999999))

            # break the loop ONLY if card is valid
            if self.get_check_sum(new_card) == True:
                break

        # call insert_account
        self.insert_account(new_card, new_pin)
        #         self.user[self.card] = self.pin

        print('Your card has been created')
        print('Your card number:')
        print(new_card)
        print('Your card PIN')
        print(new_pin)
        print()

    def setup_database(self, database_file):
        """ create a database connection to a SQLite database """
        conn = sqlite3.connect(database_file)
        try:
            conn = sqlite3.connect(self.database_file)
            cur = conn.cursor()
            sql = """
            CREATE TABLE IF NOT EXISTS card(
                id   INTEGER PRIMARY KEY,
                number TEXT,
                pin  TEXT,
                balance INTEGER DEFAULT 0)"""
            cur.execute(sql)
            conn.commit()


        except Error as e:
            print(e)

        finally:
            conn.close()

    def insert_account(self, new_card, new_pin ):

        conn = sqlite3.connect(self.database_file)
        try:
            cur = conn.cursor()
            sql = f"""INSERT INTO card(number, pin) VALUES('{new_card}', '{new_pin}')"""
            cur.execute(sql)
            conn.commit()


        except Error as e:
            print(e)

        finally:
            conn.close()

    def login(self):
        user_card = input('Enter Card Number: ').strip()
        pin = input('Enter Pin: ').strip()

        try:
            # this just means that there is a user / pin pair in our system
            if self.verify_account(user_card, pin):
                print('You have successfully logged in!')
                self.logged_on = True
                self.user = [user_card, pin]
            else:
                print('Wrong card number or PIN!')
        except KeyError:
            print('Wrong card number or PIN!')

    def verify_account(self, card, pin= '', check_pin = True):
        conn = sqlite3.connect(self.database_file)
        verified = False
        sql = ''
        try:
            cur = conn.cursor()
            if check_pin == True:
                sql = f"""
                    SELECT * 
                    FROM card
                    WHERE number = '{card}'
                    AND pin = '{pin}'
                    """
            else:
                sql = f"""
                    SELECT * 
                    FROM card
                    WHERE number = '{card}'
                    """

            cur.execute(sql)
            if len(cur.fetchall()) == 1:
                verified = True

            conn.commit()
            return verified

        except Error as e:
            print(e)

        finally:
            conn.close()

    def get_check_sum(self, card_string):
        int_list = [int(x) for x in card_string]

        # step 1: start from right most digit, double value of every other digit
        int_list.reverse()

        for i in range(len(int_list)):
            if i % 2 == 0:
                pass
            else:
                # step 2: if doubling results in a number > 9, we add the two digits of the sum
                doubled = int_list[i] * 2

                if doubled > 9:
                    reduced = int(str(doubled)[0]) + int(str(doubled)[1])
                    int_list[i] = reduced
                else:
                    int_list[i] = doubled

        return sum(int_list) % 10 == 0

    def deposit_in_account(self, card, amount, output=True):

        try:
            conn = sqlite3.connect(self.database_file)
            cur = conn.cursor()
            sql = f"""
                UPDATE card 
                SET balance = balance + {amount}
                WHERE number = '{card}'
    
                """
            cur.execute(sql)
            conn.commit()

            if output == True:
                print('Success!')

        except Error as e:
            print(e)

        finally:
            conn.close()

    def verify_transfer(self, from_card, to_card):
        if self.get_check_sum(to_card) == False:

            print('Probably you made a mistake in the card number. Please try again!')
            return False

        elif self.verify_account(to_card,check_pin=False) == False:
            print('Such a card does not exist.')
            return False

        elif to_card == from_card:

            print("You can't transfer money to the same account!")
            return False
        else:
            return True

    def transfer_to_account(self, from_card, to_card, transfer_amount):
        """Will transfer 'amount' out of from_card into to_card
        will prompt if insufficient funds"""

        if self.get_balance(from_card) < transfer_amount:
            print('Not enough money!')
        elif self.verify_transfer(from_card, to_card):
            self.deposit_in_account(card=to_card, amount=transfer_amount, output = False)
            self.withdrawal_from_account(from_card, transfer_amount, output=False)
            print('Success!')

    def close_account(self,card, pin):
        '''Close account: should allow user to delete account from database'''
        conn = sqlite3.connect(self.database_file)
        try:

            cur = conn.cursor()
            sql = f"""
            DELETE 
            FROM card
            WHERE number = '{card}'
            AND pin = '{pin}'
    
            """
            cur.execute(sql)
            conn.commit()

            logged_on = False
            print('The account has been closed!')

        except Error as e:
            print(e)

        finally:
            conn.close()

    def withdrawal_from_account(self, card, amount, output=True):

        try:
            conn = sqlite3.connect(self.database_file)
            cur = conn.cursor()
            sql = f"""
                UPDATE card 
                SET balance = balance - {amount}
                WHERE number = '{card}'
    
                """
            cur.execute(sql)
            conn.commit()

            if output == True:
                print('Success!')

        except Error as e:
            return False

        finally:
            conn.close()



newBank = EZBank()
newBank.start_menu()
