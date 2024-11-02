# functionality
#   - Student loan calculator
#       - Monthly payment
#       - interest rate
#       - edge case: if monthy payment isn't feasable
#       - disposable income
#       - out of state and instate

class StudentInterestCalculator:
    def __init__(self, principal, rate=5.0, time=1):
        """
        Initialize the calculator with principal, rate, and time.
        Default interest rate is 5% and default time is 1 year.
        """
        self.principal = principal
        self.rate = rate
        self.time = time

    def calculate_interest(self):
        """
        Calculate simple interest based on principal, rate, and time.
        """
        return (self.principal * self.rate * self.time) / 100

    def calculate_total_amount(self):
        """
        Calculate the total amount after adding interest to the principal.
        """
        return self.principal + self.calculate_interest()

    def calculate_monthly_payment(self, number_of_months):
        """
        Calculate monthly payment to repay the principal and interest over a given number of months.
        """
        interest = self.calculate_interest()
        return (self.principal + interest) / number_of_months

    def calculate_compound_interest(self, number_of_times_compounded_per_year):
        """
        Calculate compound interest given the number of times interest is compounded per year.
        """
        return self.principal * ((1 + (self.rate / (number_of_times_compounded_per_year * 100))) ** (number_of_times_compounded_per_year * self.time)) - self.principal

    def calculate_loan_amortization(self, payment_number, total_payments):
        """
        Calculate the remaining balance of a loan after a certain number of payments.
        Assumes monthly payments.
        """
        rate_per_period = self.rate / 100 / 12
        monthly_payment = self.calculate_monthly_payment(total_payments)
        remaining_balance = self.principal * ((1 + rate_per_period) ** payment_number) - monthly_payment * (((1 + rate_per_period) ** payment_number - 1) / rate_per_period)
        return remaining_balance

    def calculate_monthly_savings(self, goal_amount, months):
        """
        Calculate monthly savings required to reach a goal amount within a given number of months.
        """
        return goal_amount / months

    def calculate_effective_annual_rate(self, compounding_periods_per_year):
        """
        Calculate the effective annual rate (EAR) given the number of compounding periods per year.
        """
        return ((1 + (self.rate / compounding_periods_per_year) / 100) ** compounding_periods_per_year) - 1

    # Budgeting Methods
    def calculate_monthly_budget(self, monthly_income, fixed_expenses):
        """
        Calculate the remaining budget after subtracting fixed expenses from monthly income.
        """
        return monthly_income - fixed_expenses

    def calculate_monthly_savings_goal(self, goal_amount, months):
        """
        Calculate monthly savings needed to reach a financial goal within a certain number of months.
        """
        return goal_amount / months

    def calculate_emergency_fund(self, monthly_expenses, months_of_coverage):
        """
        Calculate the emergency fund required to cover a given number of months of expenses.
        """
        return monthly_expenses * months_of_coverage

    def calculate_category_allocation(self, monthly_income, percentage):
        """
        Calculate the allocation for a specific category based on a percentage of monthly income.
        """
        return (monthly_income * percentage) / 100

    def calculate_debt_repayment(self, total_debt, monthly_rate, months):
        """
        Calculate monthly debt repayment required to clear a total debt within a given number of months.
        """
        monthly_interest = (monthly_rate / 100) * total_debt
        return (total_debt + monthly_interest) / months

    def calculate_remaining_balance(self, initial_amount, spent_amount):
        """
        Calculate the remaining balance after spending a given amount from an initial amount.
        """
        return initial_amount - spent_amount

    def calculate_budget_surplus_or_deficit(self, monthly_income, total_expenses):
        """
        Calculate whether there is a budget surplus or deficit given income and expenses.
        """
        return monthly_income - total_expenses

    # Setters
    def set_principal(self, principal):
        """
        Set the principal amount.
        """
        self.principal = principal

    def set_rate(self, rate):
        """
        Set the interest rate.
        """
        self.rate = rate

    def set_time(self, time):
        """
        Set the time period in years.
        """
        self.time = time

    # Getters
    def get_principal(self):
        """
        Get the principal amount.
        """
        return self.principal

    def get_rate(self):
        """
        Get the interest rate.
        """
        return self.rate

    def get_time(self):
        """
        Get the time period in years.
        """
        return self.time
   








       