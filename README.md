# 🤖 FinGenius: AI-Powered Personal Finance Advisor

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Jupyter](https://img.shields.io/badge/jupyter-notebook-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Kaggle](https://img.shields.io/badge/kaggle-capstone-20BEFF.svg)
![Gen AI](https://img.shields.io/badge/Gen%20AI-5%20Capabilities-purple.svg)
![Google Gemini](https://img.shields.io/badge/Google-Gemini-4285F4.svg)

> 🎓 **Gen AI Intensive Project**  
> An intelligent financial advisory system showcasing 5 key Gen AI capabilities: Structured Output/JSON Mode, RAG (Retrieval Augmented Generation), Embeddings, Function Calling, and LangGraph Agents.

## 🚀 Project Overview

FinGenius is an AI-powered personal finance advisor that revolutionizes how users interact with their financial data. , this system demonstrates cutting-edge generative AI capabilities applied to real-world financial challenges.

### ✨ Key Features

- **🔍 Smart Transaction Analysis**: Automatically categorizes and analyzes financial transactions using embeddings
- **💬 Conversational AI Interface**: Natural language interaction for financial queries using LangGraph agents
- **📈 Intelligent Spending Insights**: Identifies patterns and trends in financial behavior
- **🎯 Personalized Recommendations**: Tailored advice based on individual financial profiles using RAG
- **📊 Structured Financial Reports**: JSON-mode output for consistent data formatting
- **🧮 Advanced Financial Calculations**: Function calling for loans, investments, and budget planning
- **📚 Knowledge-Based Advice**: Evidence-based recommendations from financial literature

## 🎯 Problem Statement

Many individuals struggle with effective financial management, needing help with:
- Understanding spending patterns and financial behavior
- Getting personalized, accessible financial advice
- Learning financial concepts and best practices
- Creating and maintaining realistic budgets
- Planning for short and long-term financial goals

FinGenius addresses these challenges by providing an intelligent, conversational assistant that analyzes financial data and offers personalized guidance.

## 🤖 Gen AI Capabilities Demonstrated

This project showcases **5 comprehensive Gen AI capabilities**:

### 1. 📊 Structured Output/JSON Mode
- Consistent transaction categorization and analysis
- Standardized budget breakdown visualization
- Structured financial health summary reports
- Automated expense pattern detection

### 2. 🔍 RAG (Retrieval Augmented Generation)
- Financial knowledge base integration for evidence-based advice
- Retrieval of relevant financial best practices and strategies
- Access to financial regulations and terminology explanations
- Context-aware recommendations based on financial literature

### 3. 🧠 Embeddings
- Semantic understanding of transaction descriptions and patterns
- Intelligent clustering of similar expenses and spending categories
- Advanced spending pattern recognition over time periods
- Similarity search for financial concepts and advice

### 4. 🛠️ Function Calling
- Automated financial calculations (savings projections, interest calculations)
- Real-time data processing and financial metric computation
- Integration capabilities for external financial data sources
- Advanced budget allocation and optimization algorithms

### 5. 🤖 Agents with LangGraph
- Sophisticated conversational financial advisor workflow
- Multi-step financial planning and goal-setting processes
- Intelligent decision trees for personalized recommendations
- Stateful conversation management across financial topics

## 📁 Project Structure

```
fingenius-ai-financial-advisor/
├── 📓 fingenius-notebook-gemini-agent.ipynb    # 🌟 Main implementation (RECOMMENDED)
├── 🐍 install_dependencies.py                  # Dependency installation script
├── 📋 requirements.txt                         # Pinned Python dependencies
├── 🔐 .env.example                             # Environment variable template
├── 📄 project_structure.md                     # Detailed technical documentation
├── 📄 LICENSE                                  # MIT License
├── 📄 .gitignore                               # Python/Jupyter gitignore
├── 📄 .gitattributes                           # Git attributes configuration
└── 📄 README.md                                # This file
```

## 🛠️ Installation & Quick Start

### Prerequisites
- Python 3.8+ 🐍
- Jupyter Notebook or JupyterLab 📓
- Google API Key (for Gemini AI) 🔑

### 🚀 Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anujdevsingh/fingenius-ai-financial-advisor.git
   cd fingenius-ai-financial-advisor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or use the installer script:
   ```bash
   python install_dependencies.py
   ```

3. **Set up your Google API Key:**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Copy `.env.example` to `.env` and add your key:
     ```bash
     cp .env.example .env
     # Edit .env and add your GOOGLE_API_KEY
     ```

4. **Launch Jupyter Notebook:**
   ```bash
   jupyter notebook
   ```

5. **🌟 Start with the main notebook:**
   - Open `fingenius-notebook-gemini-agent.ipynb` for the complete implementation
   - This notebook contains all 5 Gen AI capabilities and is the most comprehensive

## 🧪 Main Notebook Features

The **`fingenius-notebook-gemini-agent.ipynb`** notebook (334KB) includes:

| Feature | Implementation | Status |
|---------|----------------|--------|
| **📊 Structured Output/JSON Mode** | Transaction categorization, budget reports | ✅ Complete |
| **🔍 RAG (Retrieval Augmented Generation)** | Financial knowledge base integration | ✅ Complete |
| **🧠 Embeddings** | Semantic transaction analysis | ✅ Complete |
| **🛠️ Function Calling** | Financial calculations & data processing | ✅ Complete |
| **🤖 Agents with LangGraph** | Conversational financial advisor workflow | ✅ Complete |

### 🏆 **This is your complete Gen AI showcase** - all 5 capabilities in one comprehensive notebook!

## 💡 Usage Examples

The main notebook demonstrates comprehensive financial scenarios:

### 📊 **Transaction Analysis**
```python
# Automatic categorization and pattern recognition
transactions = load_financial_data()
insights = analyze_spending_patterns(transactions)
```

### 💬 **Conversational Financial Advice**
```python
# Natural language financial queries
response = financial_advisor.query("How should I budget my $5000 monthly income?")
```

### 🧮 **Financial Calculations**
```python
# Automated loan and investment calculations
mortgage_payment = calculate_loan_payment(300000, 0.045, 30)
investment_growth = calculate_investment_return(10000, 0.08, 20)
```

### 📈 **Spending Insights**
```python
# Pattern detection and recommendations
patterns = find_spending_patterns(transaction_embeddings)
recommendations = generate_budget_advice(patterns, financial_goals)
```

## 🔒 Security & Privacy

- ✅ **Secure API Key Handling**: Uses environment variables and secure client methods
- ✅ **No Hardcoded Secrets**: All sensitive information properly externalized  
- ✅ **Synthetic Data**: All examples use generated/sample data for demonstrations
- ✅ **Privacy Best Practices**: Follows financial data handling guidelines

## 🌟 Real-World Applications

### 🏦 **Financial Services**
- Personal banking applications with AI-powered insights
- Credit union member financial wellness programs
- Robo-advisor platforms with conversational interfaces

### 📱 **Fintech Solutions**
- Mobile budgeting apps with intelligent categorization
- Investment platforms with personalized advice
- Expense tracking with automated pattern recognition

### 🎓 **Financial Education**
- Educational platforms teaching financial literacy
- Personal finance coaching tools
- Financial planning software for advisors

### 🌍 **Financial Inclusion**
- Accessible financial advice for underserved populations
- Multilingual financial guidance systems
- Microfinance and community banking solutions

## 🚧 Technical Implementation

### 🔧 **Technology Stack**
- **AI Framework**: Google Gemini 2.0 Flash-Lite
- **Agent Framework**: LangGraph 0.6.11
- **Vector Database**: ChromaDB 1.5.7
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Environment**: Jupyter Notebooks

### 📈 **Performance Features**
- Automated retry mechanisms for API calls
- Exponential backoff for rate limit handling
- Efficient embedding-based similarity search
- Optimized function calling workflows

## 🔮 Future Enhancements

### 🚀 **Technical Improvements**
- [ ] Real-time financial data integration (APIs for banks/cards)
- [ ] Advanced ML models for fraud detection
- [ ] Multi-language support for global accessibility
- [ ] Mobile app development with React Native/Flutter

### 💼 **Business Features**
- [ ] Goal-based financial planning modules
- [ ] Investment portfolio optimization
- [ ] Tax optimization strategies
- [ ] Retirement planning calculators

### 🔐 **Enterprise Features**
- [ ] End-to-end encryption for sensitive data
- [ ] Compliance with financial regulations (PCI DSS, GDPR)
- [ ] Multi-tenant architecture for scalability
- [ ] Advanced analytics dashboard for financial advisors

## 🤝 Contributing

This project was developed as an educational capstone, but contributions are welcome!

### 🛠️ **How to Contribute**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 💡 **Contribution Ideas**
- Additional financial calculation functions
- Enhanced visualization capabilities
- New Gen AI capability demonstrations
- Performance optimizations
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **🤖 Google**: For providing the powerful Gemini AI platform
- **🔗 LangChain Community**: For the incredible agent framework and tools
- **🌟 Open Source Community**: For the various libraries and tools used
- **🎯 IITM BS Data Science Program**: For the educational foundation

## 📞 Connect & Support

- 🐙 **GitHub**: [Open an issue](https://github.com/anujdevsingh/fingenius-ai-financial-advisor/issues) for questions or suggestions


---

<div align="center">

**⭐ If FinGenius helps with your financial AI projects, please star this repository! ⭐**

*Built with ❤️ for the Gen AI community*

![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=fingenius-ai-financial-advisor)

</div>

## 👨‍💻 Author

<div align="center">

### **Anuj Dev Singh** 
*AI/ML Enthusiast | Data Science Student | Gen AI Developer*

</div>


---

*"Bridging the gap between advanced AI technology and practical financial solutions for everyone."*

## 📄 License 