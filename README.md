# Movie Recommendation System

## Overview

This project is a semester-long group assignment focused on building, deploying, and monitoring a movie recommendation system. The project simulates an early-stage streaming service that serves personalized movie recommendations to users. The system is designed to handle a dataset of approximately 1 million users and 27,000 movies, considering real-world challenges like scalability, reliability, and model drift.

## Features

- **Collaborative Filtering-Based Recommendation Model**: Implements multiple recommendation techniques, including user-based and item-based collaborative filtering.
- **Model Deployment**: Serves predictions via a REST API using Flask.
- **Performance Metrics**: Evaluates model accuracy, training/inference costs, and model size.
- **Infrastructure and Automation**: Includes automated data pipelines, testing, and continuous integration with GitHub Actions.
- **Monitoring and Scaling**: Uses logging, telemetry, and containerized deployments for high availability.
- **Fairness & Security Analysis**: Assesses biases, feedback loops, and potential security vulnerabilities.