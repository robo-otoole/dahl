################################################################################
#In this section we import library code to help us do things

#this library is used to generate a random number so we can choose questions randomly
import random

#library for working with the keypad
from machine import Pin

#library allows us to add timed delays
import time

#library for working with the LCD screen
from lcd1602 import LCD

################################################################################
#Next we set up the keypad

# Create a map between keypad buttons and characters
matrix_keys = [['1', '2', '3', 'A'],
               ['4', '5', '6', 'B'],
               ['7', '8', '9', 'C'],
               ['*', '0', '#', 'D']]

# PINs according to schematic - Change the pins to match with your connections
keypad_rows = [9,8,7,6]
keypad_columns = [5,4,3,2]

# Create two empty lists to set up pins ( Rows output and columns input )
col_pins = []
row_pins = []


# Loop to assign GPIO pins and setup input and outputs
for x in range(0,4):
  row_pins.append(Pin(keypad_rows[x], Pin.OUT))
  row_pins[x].value(1)
  col_pins.append(Pin(keypad_columns[x], Pin.IN, Pin.PULL_DOWN))
  col_pins[x].value(0)

################################################################################
#THIS IS WHERE WE DEFINE A CLASS FOR MULTIPLE CHOICE QUESTIONS
#MCQs HAVE A QUESTION PROPERTY, A LIST OF POSSIBLE ANWERS, AND THE INDEX OF THE CORRECT ANSWER

class mcq:
    def __init__(self, question, answers, correct):
      self.question = question
      self.answersList = answers.split("|")
      self.answersCount = len(self.answersList)
      self.correct = correct
    def getQuestion(self):
      return self.question
    def getAnswer(self, index):
      return self.answersList[index]
    def getAnswers(self):
      return answersList
    def isCorrect(self, choice):
      if choice == self.correct:
        return True 
      else:
        return False

################################################################################
#create an lcd object to access the LCD hardware
lcd = LCD()

################################################################################
#Method for writing neatly to both lines of the LCD and waiting for key input to continue
#The keypad has two lines of 16 characters, and doesn't auto-wrap, so we need to split manually

def writeToLCD(message, wait):
    lcd.clear()
    if len(message) > 16: #if lines are too long
      lcd.message(message + '\n'[:16]) #this does the splitting
      message2 = message[16:len(message)]
      message2 = message2.strip()
      lcd.message(message2)
    else:
      lcd.message(message)
    if wait == True: #in most cases we want to wait for a keypress before moving on
      while True:
        for row in range(4):
          for col in range(4):
              row_pins[row].high()
              key = None
              if col_pins[col].value() == 1:
                row_pins[row].low()
                time.sleep(1)
                return False
    

################################################################################
#THIS FUNCTION IS USED TO LOAD CSV DATA FROM A FILE

def loadCSV(path):
  csvdata = []
  delim = ',' #the data is comma separated
  with open(path,'r') as file:
    for line in file:
      csvdata.append(line.rstrip('\n').rstrip('\r').split(delim))
  return csvdata

#HERE WE ARE LOADING THE QUESTIONS FROM A FILE IN WHICH THEY ARE SPECIFIED USING CSV FORMAT

def loadQuestionsFromCSV():
  global questions
  global questionCount #this is so we now how many questions there are to ask
  global startingCount
  questionCount = 0
  data = loadCSV("./test.csv") #that's the file
  for row in data:
    question = mcq(row[1], row[2], row[0]) #creating a question object from the data
    questions.append(question) #adding the new question to the lost of questions
    questionCount = questionCount + 1
  startingCount = questionCount


################################################################################
#THIS METHOD SELECTS A QUESTION AT RANDOM AND DISPLAYS IT

def askRandomQuestion():
  global questionCount
  global score
  #GET A RANDOM INDEX NUMBER WITHIN THE BOUNDS OF THE QUESTION SET
  if questionCount > 0:
    index = random.randint(0, questionCount - 1)
  else:
    index = 0
  #GET THE QUESTION AT THAT INDEX  
  selectedQuestion = questions[index]
  #NOW REMOVE THE QUESTION FROM AVAILABLE QUESTIONS
  questions.pop(index)
  questionCount = questionCount - 1 #we've asked a question, so reduce the number left to ask
  writeToLCD(selectedQuestion.getQuestion(), True)
  answerCount = 1
  for i in selectedQuestion.answersList:
    writeToLCD(str(answerCount) + " " + i, True)
    answerCount = answerCount + 1
  writeToLCD("Enter a number", False)
  x = True
  while x == True:
     for row in range(4):
        for col in range(4):
            row_pins[row].high()
            key = None
            if col_pins[col].value() == 1:
                #print("You have pressed:", matrix_keys[row][col])
                if selectedQuestion.isCorrect(matrix_keys[row][col]):
                  writeToLCD("Correct", True)
                  score = score + 1
                else:
                  writeToLCD("Wrong", True)
                #print ("\033c")
                key_press = matrix_keys[row][col]
                time.sleep(0.3)
                x = False
        row_pins[row].low()
#LOOP THROUGH ASKING QUESTIONS AT RANDOM UNTIL NONE LEFT
  if questionCount > 0:
    askRandomQuestion()
  else:
    writeToLCD("Done. You scored " + str(score) +  " out of " + str(startingCount) + "\n\n\n", True)


################################################################################
#This is where the action actually starts

questions = list()

score = 0

loadQuestionsFromCSV()

writeToLCD("Press any key to start", True)

#ASK THE FIRST QUESTION
askRandomQuestion()

