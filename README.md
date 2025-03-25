# Overview

The scope of this test is to evaluate your knowledge of making Telegram bots with Python, storing data on a Mongo 
back-end. The key elements of the test are functionality, usability, that the flow of the prompts works as described.

Usability, as in a good user experience, is a key factor: all the flows should work as described but also, for example, not leave buttons behind that are no longer relevant and not overwrite information that the user needs to see.

# Task

The bot is a simple mock banking application bot. Upon typing `/start`, the user should get a prompt with three inline buttons:

- Check Balance
- Deposit
- Withdraw

## Check Balance

Posts a message showing the user's balance. The balance starts at 0.

It should also tell the user the time the last deposit or withdrawal was made, and for what amount.

## Deposit

A multi-step process.

The first prompt asks how much the user wants to deposit. They can reply by typing a number (e.g. 100). It must 
validate that it's an integer > 0 and let user type another number if it's not valid.

The second prompt asks them to confirm the deposit for the given amount. They can "Confirm" or "Cancel".

Once "Confirm" it adds that amount to their balance and stores a record of the transaction.

## Withdraw

Withdraw is the same as Deposit, except:

- The amount withdrawn must be smaller than their balance
- Once completed it removes from their balance instead of adding.

# Deliverable

A working Telegram bot that does the above, written in Python, using Mongo as a back-end.

Provide us with the bot's username and run it from your end, so that we can test that it works.

Provide us with the source code so we can evaluate it. Time taken is a factor, and we'll count the
time from giving this link to receiving the code as the completion time.

# Extra Credit

Once you've completed the basic bot, for extra credit you can add the following layer of complexity.

Be sure to send us the code for the basic task first so we can evaluate the timing separately for the basic
bot and the extra credit.

## Deposit/Withdrawal Methods

After entering the deposit amount, instead of asking user to confirm right away, instead ask the user to
pick the method they used to deposit.

Each user has their own list of deposit methods that
starts empty. There should be an inline button for each method, and a button "Add New Method" which lets the user add a new method and continues the flow
with it selected.

Add the same step to the withdrawal flow, together with the "Add New Method" button. The same method is usable for both deposits and withdrawals.

The user should be able to cancel the deposit or withdrawal at any step: entering amount, choosing deposit method, adding new method, or confirming at the end.

## Add New Method

This is selected from the Deposit or Withdrawal flow.

The first prompt asks them the type of method. There are inline buttons for Bank Transfer, Paypal, Crypto. 

For Bank Transfer, it asks them for the name of the bank. User types a response (e.g. "Chase") and the method
is added to their method list.

For Paypal, it asks them for their Paypal e-mail address, and adds the method to the list.

For Crypto, is asks them to choose between BTC, ETH, or USDT. Then it asks them for the crypto address, and then it 
saves the method to their list.

Once the method is added, the deposit/withdrawal flow should continue as if they had selected the method. On
future deposits or withdrawals, the method should appear with its description as one of a list of inline buttons.

Each method can be used for both depositing and withdrawing. The user may have multiple methods but they still have only one balance. They can deposit 100 with PayPal and then withdraw 100 with Crypto. 

## Deliverable

Once the above is done, hand off the working code and updated bot that we can use to test, as before.
