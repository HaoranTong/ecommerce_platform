import axios from 'axios';

export interface Member {
  id: number;
  // 会员相关接口定义将在后续开发中完善
}

export const getMembers = (params: { search?: string; page?: number; limit?: number }) => {
  return axios.get<Member[]>('/member-system/members', { params });
};
