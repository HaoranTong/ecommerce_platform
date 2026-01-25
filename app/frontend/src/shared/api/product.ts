import axios from 'axios';

export interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
  status: 'draft' | 'published' | 'archived';
}

export const getProducts = (params: { search?: string; page?: number; limit?: number }) => {
  return axios.get<Product[]>('/product-catalog/products', { params });
};
