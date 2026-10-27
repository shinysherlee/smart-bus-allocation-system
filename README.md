\# Smart Bus Allocation System



\## Project Overview

The Smart Bus Allocation System is a Python and Streamlit application that demonstrates how spare buses can be allocated across existing Chennai bus routes based on simulated passenger demand.



The project compares two approaches:

\- \*\*Greedy Algorithm:\*\* Selects a route based on its current priority.

\- \*\*Heap-Based Algorithm:\*\* Uses a priority queue to select routes efficiently.



\## Features

\- Chennai bus route data exploration

\- Simulated passenger demand and crowd reports

\- Configurable bus capacity and spare bus availability

\- Greedy and heap-based allocation comparison

\- Route stops table and map visualization

\- Unit tests for allocation logic



\## Technologies Used

\- Python

\- Streamlit

\- Pandas

\- Python `heapq`

\- Unit testing



\## Project Structure

```text

smart\_bus\_allocation\_system/

├── app.py

├── allocation.py

├── allocation\_heap.py

├── data\_loader.py

├── test\_allocation.py

├── check\_routes.py

├── requirements.txt

├── README.md

└── data/

&#x20;   └── mtc/

```



\## Setup and Run



1\. Install Python.

2\. Open a terminal in the project directory.

3\. Install dependencies:



&#x20;  ```bash

&#x20;  pip install -r requirements.txt

&#x20;  ```



4\. Start the application:



&#x20;  ```bash

&#x20;  python -m streamlit run app.py

&#x20;  ```



\## Run Tests



```bash

python -m unittest -v test\_allocation.py

```



\## Dataset

The project uses a community-maintained Chennai GTFS dataset:

https://github.com/ungalsoththu/ChennaiGTFS



Check the dataset's licence and redistribution terms before committing the dataset files to a public repository.



\## Limitations

\- Passenger demand and crowd reports are simulated.

\- The application does not connect to live bus tracking or real-time passenger feeds.

\- Allocation results are demonstrations and should not be interpreted as official Chennai bus service decisions.

\- Route and stop data may be incomplete or outdated.



\## Future Improvements

\- Integrate verified real-time passenger demand data.

\- Add estimated travel times and operating costs.

\- Improve allocation evaluation using additional performance metrics.

\- Add route-level demand visualization.



\## Testing

The allocation test suite has been run using Python's built-in `unittest` framework.



\## Disclaimer

This is an educational college project and is not an official Chennai bus allocation system.

