************************************************************
*                                                          *
*             SIMULATORS FOR SEMI-PERSISTENT              *
*            SCHEDULING IN C-V2X MODE 4 SIMULATOR            *
*                                                          *
************************************************************

Welcome to the Simulators-for-SPS repository!
------------------------------------------------

This project is a simulator for semi-persistent scheduling (SPS) in C-V2X Mode 4, designed with flexibility and extensibility in mind. The simulator is ideal for researchers and developers who want to evaluate SPS performance under various vehicular network scenarios.

------------------------
Project Overview
------------------------
•  **Purpose:**  
   Simulate SPS in C-V2X Mode 4 with default parameters based on 20Hz beacon broadcasting.
   
•  **Key Features:**  
   - Object-Oriented Programming (OOP) design to ease extension and integration.
   - Fine-grained simulation operating at the millisecond level.
   - Configurable parameters including transmit power, beacon range, beacon rate, reselection counter range, and accessible resource ratio.
   - Use of Python’s argparse.ArgumentParser for robust command-line argument parsing.

•  **Enhanced OOP Version:**  
   The latest OOP update (located in the `OOP_for_SPS` folder) provides a cleaner, more extendable codebase with improved simulation detail and flexibility.

------------------------
Installation & Requirements
------------------------
To get started, clone the repository:
    
    git clone https://github.com/alexisyanez/Simulators-for-SPS.git

Ensure you have:
   - Python 3.x installed on your machine.
   - Required Python packages (if any) – check the `simulations.py` file for dependencies or include a requirements.txt file for convenience.

------------------------
Usage Instructions
------------------------
1. **Basic Simulation:**  
   Run the simulator using the main script. For example:
   
       python simulations.py --param1 value1 --param2 value2

2. **Customizing the Simulation:**  
   Edit `simulations.py` to modify default parameters such as:
   - Transmit power
   - Beacon range
   - Beacon rate
   - Reselection counter range
   - Accessible resource ratio

3. **OOP Version:**  
   For a more advanced simulation with a finer granularity, check out the `OOP_for_SPS` folder. This version uses millisecond-level simulation and is structured for easier extension.

------------------------
Examples
------------------------
• **Running a default simulation:**  
   Simply execute:
   
       python simulations.py

• **Running with custom parameters:**  
   Use the command-line options to adjust the simulation parameters. For example:
   
       python simulations.py --beacon_rate 10 --tx_power 23

------------------------
Contributing
------------------------
Contributions are warmly welcomed! If you have suggestions, improvements, or want to extend the simulator for new applications, feel free to fork the repository and open a pull request. For major changes, please open an issue first to discuss what you would like to change.

------------------------
License
------------------------
This project is provided "as-is" without any warranty. For detailed licensing information, please refer to the LICENSE file included in the repository.

------------------------
Contact & Support
------------------------
For any questions or support, please contact:
   - Repository owner: alexisyanez
   - GitHub Issues: https://github.com/alexisyanez/Simulators-for-SPS/issues

------------------------------------------------
Happy Simulating!
------------------------------------------------

