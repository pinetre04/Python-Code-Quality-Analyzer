
import ast
import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Code Quality Analyzer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Python Code Quality Analyzer")
st.write("AST 기반 Python 소스코드 정적 분석 및 품질 평가 시스템")
st.divider()


# Count decision points in a function
def calculate_complexity(func):
    complexity = 1

    for node in ast.walk(func):
        if node is not func and isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue

        if isinstance(
            node,
            (ast.If, ast.For, ast.AsyncFor,
             ast.While, ast.ExceptHandler,
             ast.IfExp)
        ):
            complexity += 1

        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1

    return complexity


# Analyze a Python source file
def analyze_code(source):
    tree = ast.parse(source)
    nodes = list(ast.walk(tree))

    functions = [
        node for node in nodes
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        )
    ]

    classes = [
        node for node in nodes
        if isinstance(node, ast.ClassDef)
    ]

    results = []
    issues = []

    for func in functions:
        length = func.end_lineno - func.lineno + 1
        complexity = calculate_complexity(func)
        has_docstring = ast.get_docstring(func) is not None

        results.append({
            "Function": func.name,
            "Start Line": func.lineno,
            "Lines": length,
            "Complexity": complexity,
            "Docstring": "Yes" if has_docstring else "No"
        })

        if length > 50:
            issues.append({
                "Line": func.lineno,
                "Function": func.name,
                "Severity": "Warning",
                "Issue": "Function exceeds 50 lines"
            })

        if complexity > 10:
            issues.append({
                "Line": func.lineno,
                "Function": func.name,
                "Severity": "Warning",
                "Issue": "High cyclomatic complexity"
            })

        if not has_docstring:
            issues.append({
                "Line": func.lineno,
                "Function": func.name,
                "Severity": "Info",
                "Issue": "Missing docstring"
            })

    summary = {
        "lines": len(source.splitlines()),
        "functions": len(functions),
        "classes": len(classes),
        "issues": len(issues)
    }

    return summary, results, issues


# File upload interface
uploaded_file = st.file_uploader(
    "분석할 Python 파일을 업로드하세요.",
    type=["py"]
)

if uploaded_file is not None:
    try:
        source_code = uploaded_file.getvalue().decode("utf-8-sig")
        summary, results, issues = analyze_code(source_code)

    except UnicodeDecodeError:
        st.error("UTF-8 형식의 Python 파일을 업로드하세요.")

    except SyntaxError as error:
        st.error(
            f"Syntax Error: Line {error.lineno} - {error.msg}"
        )

    else:
        st.success("Code analysis completed successfully!")

        st.subheader("Code Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Lines", summary["lines"])
        col2.metric("Functions", summary["functions"])
        col3.metric("Classes", summary["classes"])
        col4.metric("Issues", summary["issues"])

        st.divider()
        st.subheader("Function Analysis")

        if results:
            st.dataframe(
                pd.DataFrame(results),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No functions found.")

        st.divider()
        st.subheader("Code Quality Report")

        if issues:
            issue_df = pd.DataFrame(issues)

            st.dataframe(
                issue_df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                label="Download Quality Report (CSV)",
                data=issue_df.to_csv(index=False).encode("utf-8-sig"),
                file_name="quality_report.csv",
                mime="text/csv"
            )
        else:
            st.success("No issues detected by the configured rules.")

        st.divider()
        st.subheader("Source Code Preview")

        st.code(source_code, language="python")
