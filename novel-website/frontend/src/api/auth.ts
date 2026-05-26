import apiClient from './index'
import type { LoginRequest, RegisterRequest, TokenResponse, UserResponse } from '@/types'

export const loginApi = (data: LoginRequest) =>
  apiClient.post<TokenResponse>('/auth/login', data)

export const registerApi = (data: RegisterRequest) =>
  apiClient.post<TokenResponse>('/auth/register', data)

export const fetchProfileApi = () =>
  apiClient.get<UserResponse>('/users/me')

export const refreshTokenApi = () =>
  apiClient.post<TokenResponse>('/auth/refresh')