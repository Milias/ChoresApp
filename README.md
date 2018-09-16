#ChoresApp

A program for bookkeeping and chores tracking.

#About

* Edit icon (edit.svg) created by Icons fest from the Noun Project.
* Check icon (check.svg) created by Johan Ronsse from the Noun Project.
* Add icon (add.svg) created by Gautam Arora from the Noun Project.
* Delete icon (edit.svg) created by lipi from the Noun Project.
* View icon (view.svg) created by Edward Boatman from the Noun Project.
* TEX File by Viktor Vorobyev from the Noun Project.

#Usage

- Start the program
  - For the first time run "install.sh"
  - Then, execute "run.sh"

- Bill
  - Update payments from bank
    - Go to Billing > Transactions
    - For each payment in the bank account:
      - "+" (Plus) button, for adding a transaction
      - Select "Payment" in first drop-down list
      - Select correct name in second drop-down list
      - "Description" is optional
      - Select date of transaction (month/day/year)
      - Set amount
      - "Save"
    - Spotify payments
      - Add transaction (Payment)
      - Select correct person
      - Set any date in the period of the bill
      - Set amount to -6 euros per person
      - For the person paying to Spotify, set amount to 6 times number of people
  - Expenses
    - For each expense in table:
      - Add transaction (expense)
      - Select correct name, description, date and amount
  - Chores (assignments)
    - Go to House > Assignments
    - For each week, click on the three sliders button to edit
    - Set people "Home" status (yes or no)
    - To add extra chores (such as "Clean microwave"):
      - Go to the last three spots
      - With "(anyone)" as the person, select the Chore
      - "Save"
      - Go back to editing that week
    - If a chore is done by more than one person, select them by Control + Click
  - Finishing the bill
    - Go to Billing > Bills, and click "+"
    - Set start date to +1 day of the previous bill (Tuesday)
    - Set end date to last Sunday of the bill
    - Set recurring to 36 euros
    - Check amounts
    - Go back to Billing > Bills and click on file with "</>" icon to download latex file
    - Once everything is fixed, click on the airplane button
  - New expenses table
    - Go to Billing > Expenses
    - Pick start date first Monday after last bill
    - Pick end date last Sunday eight or nine weeks in the future
    - Click "Generate" to download the tex file

