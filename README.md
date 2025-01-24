# projectA

## Purpose of the project:

This is a side project aimed at simplifying my wife's workday. 

It will primarily focus on automating repetitive tasks, such as file splitting and other processes she currently performs manually.

## What's the procedure?

The script will mimic the actions a human would take, for example:

1. **Login:**  Authenticate to the relevant system.
2. **Press Icon A:**  Click on a specific icon within the interface.
3. **Choose Folder X from Scroll Bar:** Navigate through a list of folders using a scroll bar and select a specific folder.
4. **Press Button C:** Click on a designated button labeled "C" to initiate the desired action.

## Idea:

1. Utilize `pyautogui` to record and replay mouse and keyboard actions, effectively automating the human workflow.
2. Package the final release as a portable executable (.exe) for easy execution by users without requiring Python installation.

## Action plan:

1. **Survey PyAutoGUI Usage:**  Explore the functionalities and limitations of `pyautogui` to determine its suitability for the project.
2. **Build the Flowchart:** Create a detailed flowchart outlining each step of the automated process, ensuring clarity and accuracy.
3. **Coding:** Implement the script using Python and `pyautogui`, following the defined flow chart.
4. **Testing (UT):**  Thoroughly test the script to ensure it functions correctly and produces the desired results.
5. **Release:** Package the script as a portable executable (.exe) for distribution.

## v0.3

- **UI/UX Improvements:** Implement a user interface (UI) using PyQt to enhance usability and provide a more intuitive experience.
    -  Utilize PyQt Designer to design the layout visually and convert it into Python code.
        - `python -m PyQt5.uic.pyuic your_file.ui -o your_file.py` 


pytest test_pdf_parser.py

need tesseract
brew install tesseract
brew install tesseract-lang