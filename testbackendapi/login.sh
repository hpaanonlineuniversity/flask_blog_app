#!/bin/bash

# Simple login script
curl -X POST http://localhost:5000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user01@example.com",
    "password": "password"
  }'