# Vision and Design Principles

## Vision

The vision of quant-bt is repository is to provide a comprehensive and efficient Python-based backtesting framework for intraday stock trading and compound trades like option spreads. We aim to offer a powerful toolkit that empowers its developers to analyze and test their trading strategies rigorously, while being user-friendly and flexible enough to cater to various trading styles and asset classes. Freelancers are welcome to create as many strategies for the clients.

## Costs
1. A single data could be sourced and its cost be shared among the actual users.
2. The server resource could be used on a rotation basis. A small fee (the cost) could be paid to the one who is running the server.
3. Vectorbt Pro version could be purchased and shared among the users as well, if necessary.

Please note that it is not the obligation of the dormant users to pay any charges and will remain free of charge.

## Design Principles

### Single Responsibility Principle (SRP)

Each component in the backtesting framework should have a single, well-defined responsibility. This promotes modularity and ensures that changes to one aspect of the system do not affect unrelated parts. For example, separate modules should handle data management, strategy execution, and performance evaluation.

### Open/Closed Principle (OCP)

The backtesting framework should be open for extension but closed for modification. This means that new features can be added without altering existing code. We achieve this by designing the codebase in a way that allows users to extend functionality through interfaces or plugins.

### Liskov Substitution Principle (LSP)

Any class or module within the framework that is used as a base should be substitutable by its derived classes. In the context of backtesting, this means that different trading strategies or data sources can be interchanged without altering the overall behavior of the system.

### Interface Segregation Principle (ISP)

The interfaces provided by the backtesting framework should be specific to the needs of the clients that use them. Large, monolithic interfaces should be avoided in favor of smaller, more focused ones. This ensures that clients are not forced to depend on methods they do not use.

### Dependency Inversion Principle (DIP)

High-level modules should not depend on low-level modules directly. Instead, both should depend on abstractions. In the context of backtesting, this means that the main components, such as data handling and strategy execution, should depend on interfaces or abstract classes, promoting loose coupling and easy substitution of components.

By adhering to these SOLID principles, the Python backtesting repository will have a well-structured and maintainable codebase that allows for easy extension, reduces code duplication, and enhances the overall flexibility of the framework. It encourages a systematic approach to design and facilitates collaboration among contributors by providing clear guidelines for building scalable and reliable backtesting solutions.

## Contribution

Contributions to the repository are welcome and encouraged. Whether it's bug fixes, new features, or documentation improvements, we value the community's efforts to make this backtesting framework better for everyone.

To contribute, please follow our [contribution guidelines](CONTRIBUTING.md) and adhere to our [code of conduct](CODE_OF_CONDUCT.md).

## License

This repository is licensed under the [MIT License](LICENSE), granting you the freedom to use, modify, and distribute the codebase for both commercial and non-commercial purposes.

## Disclaimer

Trading involves risk, and backtesting is not a guarantee of future results. The purpose of this repository is to provide a framework for testing and analyzing trading strategies. Users should exercise caution and do their research before implementing any strategies in real trading environments. The maintainers of this repository are not responsible for any financial losses incurred through the use of this software.

### Inspiration
[quantplay](https://www.quantplay.tech) for backtesting
[pyalgotrading](https://github.com/pannet1/pyalgotrading) for design 
