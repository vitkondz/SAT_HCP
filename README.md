# SAT Solver for Hamiltonian Cycle Problem (HCP)

## Overview

This project implements a **SAT-based solver** to determine whether a given graph contains a **Hamiltonian cycle**. The solver encodes the Hamiltonian Cycle Problem (HCP) into a **Boolean satisfiability problem (SAT)** and utilizes modern SAT solvers to find a solution efficiently.

## Background

The **Hamiltonian Cycle Problem** is a fundamental problem in graph theory and theoretical computer science. Given a graph **G = (V, E)**, the problem is determining whether a simple cycle exists that visits every vertex exactly once.

To encode HCP into SAT, I refer to the methodology described in research papers on SAT encodings of graph problems, specifically:

**"In Pursuit of an Efficient SAT Encoding for the Hamiltonian Cycle Problem"** (Main reference paper)

## Installation

### Prerequisites

If you run with PbLib, you need Python 3.9- to ensure installation. If not, you can use Python 3.10+ to install and run the project normally.

### Install dependencies

```bash
pip install -r requirements.txt
```

## Contact

For any questions or contributions, please reach out at [**vitanhv26@gmail.com**](mailto\:vitanhv26@gmail.com).

