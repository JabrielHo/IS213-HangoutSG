# HangoutSG
## Project undergoing migration from OutSystems Low Code Platform to Flask

### G10 Team 5

HangoutSG aims to connect users with similar hobby interests through both online interactions and in-person meetups. The platform serves two primary purposes: facilitating online discussions through forum posts and enabling users to organize and join real-world events. The target audience consists of hobby enthusiasts across Singapore looking to connect with others sharing their interests.


## Table of Contents

1. [Getting Started](#getting-started)
2. [Technical Overview Diagram](#technical-overview-diagram)
3. [SOA Layer Diagram](#soa-layer-diagram)
4. [Technologies Used](#technologies-used)

## Getting Started

### Prerequisites

1. Docker ([Windows](https://docs.docker.com/desktop/install/windows-install/) | [MacOS](https://docs.docker.com/desktop/install/mac-install/))

### Getting Started (Docker Compose)

1. To start the docker deployment, run the following command in the root folder:

```bash
$ docker compose up -d
```

2. To tear down the deployment, run the following command in the root folder:

```bash
$ docker compose down
```

3. To tear down the deployment and volumes, run the following command in the root folder:

```bash
$ docker compose down -v
```

## Technical Overview Diagram
<img src="./assets/technical_overview.png" alt="Technical Overview Diagram" />

## SOA Layer Diagram
<img src="./assets/SOA_layer.png" alt="vuejslogo" />

## Technologies Used

<p align="center"><strong>Frontend Stack</strong></p>
<p align="center">
    <img src="https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D" alt="vuejslogo" />
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="javascript logo" />
    <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="vite logo" />
    <img src="https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white" alt="bootstrap logo" />
</p>

<p align="center"><strong>Authentication</strong></p>
<p align="center">
    <img src="https://img.shields.io/badge/Auth0-EB5424?style=for-the-badge&logo=auth0&logoColor=white" alt="auth0 logo" />
</p>

<p align="center"><strong>Backend Stack</strong></p>
<p align="center">
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="flasklogo" />
    <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="sqlalchemy logo" />
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python logo" />
    <img src="https://img.shields.io/badge/Flask_SocketIO-010101?style=for-the-badge&logo=socket.io&logoColor=white" alt="flask socketio logo" />
    <img src="https://img.shields.io/badge/OutSystems-FF6A00?style=for-the-badge&logo=outsystems&logoColor=white" alt="outsystems logo" />
</p>

<p align="center"><strong>API Gateway</strong></p>
<p align="center">
<img src="https://img.shields.io/badge/Kong-003459?style=for-the-badge&logo=kong&logoColor=white" alt="kong logo" />
</p>

<p align="center"><strong>Storage Solutions</strong></p>  
<p align="center">
<img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="mysql logo" />
<img src="https://img.shields.io/badge/Amazon_RDS-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white" alt="aws rds logo" />
</p>

<p align="center"><strong>Message Broker</strong></p>
<p align="center">
<img src="https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white" alt="rabbitmq logo" />
</p>

<p align="center"><strong>Architecture & Design</strong></p>
<p align="center">
<img src="https://img.shields.io/badge/Microservices-666666?style=for-the-badge" alt="microservices" />
<img src="https://img.shields.io/badge/REST_API-009688?style=for-the-badge" alt="rest api" />
</p>

<p align="center"><strong>Containerization & Deployment</strong></p>
<p align="center">
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="docker logo" />
<img src="https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="docker compose logo" />
</p>
