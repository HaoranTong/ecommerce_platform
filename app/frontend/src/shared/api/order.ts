import axios from 'axios';

export interface Order {
  id: number;
  // 订单相关接口定义将在后续开发中完善
}

export const getOrders = (params: { search?: string; page?: number; limit?: number }) => {
  return axios.get<Order[]>('/order-management/orders', { params });
};
