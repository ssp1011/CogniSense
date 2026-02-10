# CogniSense — Makefile
# Common development commands

.PHONY: help setup backend frontend train test clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup:  ## Install all dependencies
	pip install -r backend/requirements.txt
	pip install -r ml/requirements.txt
	cd frontend && npm install

backend:  ## Run backend dev server
	cd backend && uvicorn app.main:app --reload

frontend:  ## Run frontend dev server
	cd frontend && npm start

train:  ## Run ML training pipeline
	python ml/training/train.py

test:  ## Run all tests
	pytest backend/tests/ -v

clean:  ## Remove generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf logs/*.log
	rm -rf ml/experiments/*
