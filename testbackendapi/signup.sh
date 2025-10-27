#!/bin/bash

# Simple signup script
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user02",
    "email": "user02@example.com",
    "password": "password"
  }'