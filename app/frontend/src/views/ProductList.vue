<template>
  <div class="product-list">
    <h1>商品列表</h1>
    
    <!-- 搜索过滤区 -->
    <n-card>
      <n-form inline :model="searchForm" @submit.prevent="handleSearch">
        <n-form-item label="商品名称">
          <n-input v-model:value="searchForm.name" placeholder="请输入商品名称" clearable />
        </n-form-item>
        <n-form-item label="分类">
          <n-select 
            v-model:value="searchForm.category_id" 
            :options="categories" 
            label-field="name" 
            value-field="id"
            placeholder="请选择分类"
            clearable
          />
        </n-form-item>
        <n-form-item label="品牌">
          <n-select 
            v-model:value="searchForm.brand_id" 
            :options="brands" 
            label-field="name" 
            value-field="id"
            placeholder="请选择品牌"
            clearable
          />
        </n-form-item>
        <n-form-item label="状态">
          <n-switch 
            v-model:value="searchForm.status" 
            checked-value="true" 
            unchecked-value="false"
            :round="false"
          >
            <template #checked>
              启用
            </template>
            <template #unchecked>
              禁用
            </template>
          </n-switch>
        </n-form-item>
        <n-form-item>
          <n-button attr-type="submit" type="primary">搜索</n-button>
        </n-form-item>
      </n-form>
    </n-card>

    <!-- 操作按钮区 -->
    <div class="actions">
      <n-button type="primary" @click="showProductModal({}, 'create')">新增商品</n-button>
    </div>

    <!-- 商品列表 -->
    <n-data-table
      :columns="columns"
      :data="products"
      :loading="loading"
      :pagination="pagination"
      remote
      @update:page="handlePageChange"
    />

    <!-- 商品表单弹窗 -->
    <n-modal v-model:show="showModal" preset="dialog" title="商品信息" style="width: 800px;">
      <n-form
        ref="formRef"
        :model="currentProduct"
        :rules="rules"
        label-placement="left"
        label-width="100"
      >
        <n-form-item label="商品名称" path="name">
          <n-input v-model:value="currentProduct.name" placeholder="请输入商品名称" />
        </n-form-item>
        
        <n-form-item label="分类" path="category_id">
          <n-select 
            v-model:value="currentProduct.category_id" 
            :options="categories" 
            label-field="name" 
            value-field="id"
            placeholder="请选择分类"
          />
        </n-form-item>
        
        <n-form-item label="品牌" path="brand_id">
          <n-select 
            v-model:value="currentProduct.brand_id" 
            :options="brands" 
            label-field="name" 
            value-field="id"
            placeholder="请选择品牌"
          />
        </n-form-item>
        
        <n-form-item label="状态" path="status">
          <n-switch v-model:value="currentProduct.status">
            <template #checked>
              启用
            </template>
            <template #unchecked>
              禁用
            </template>
          </n-switch>
        </n-form-item>
        
        <!-- SKU管理区域 -->
        <n-divider title-placement="center">SKU管理</n-divider>
        
        <div class="sku-section">
          <n-button @click="addNewSku">添加SKU</n-button>
          
          <n-data-table
            :columns="skuColumns"
            :data="currentSkus"
            :pagination="false"
            style="margin-top: 16px;"
          />
        </div>
      </n-form>
      
      <template #action>
        <n-button @click="showModal = false" style="margin-right: 10px;">取消</n-button>
        <n-button type="primary" @click="submitProduct" :loading="submitting">确定</n-button>
      </template>
    </n-modal>
    
    <!-- SKU表单弹窗 -->
    <n-modal v-model:show="showSkuModal" preset="dialog" title="SKU信息" style="width: 600px;">
      <n-form
        ref="skuFormRef"
        :model="currentSku"
        :rules="skuRules"
        label-placement="left"
        label-width="100"
      >
        <n-form-item label="规格描述" path="spec">
          <n-input v-model:value="currentSku.spec" placeholder="例如：红色, XL" />
        </n-form-item>
        
        <n-form-item label="价格(分)" path="price">
          <n-input-number v-model:value="currentSku.price" :min="0" />
        </n-form-item>
        
        <n-form-item label="库存" path="stock">
          <n-input-number v-model:value="currentSku.stock" :min="0" />
        </n-form-item>
      </n-form>
      
      <template #action>
        <n-button @click="showSkuModal = false" style="margin-right: 10px;">取消</n-button>
        <n-button type="primary" @click="saveSku">确定</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue';
import {
  NButton,
  NCard,
  NDataTable,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSelect,
  NSwitch,
  NImage,
  NModal,
  NDivider,
  useMessage
} from 'naive-ui';
import axios from 'axios';

interface Product {
  id: number;
  name: string;
  category_id: number;
  brand_id: number;
  status: boolean;
  cover_image: string;
  created_at: string;
}

interface Category {
  id: number;
  name: string;
}

interface Brand {
  id: number;
  name: string;
}

interface Sku {
  id?: number;
  product_id?: number;
  spec: string;
  price: number;
  stock: number;
}

const message = useMessage();
const loading = ref(false);
const submitting = ref(false);
const showModal = ref(false);
const showSkuModal = ref(false);

// 搜索表单
const searchForm = ref({
  name: '',
  category_id: null,
  brand_id: null,
  status: null
});

// 当前商品和SKU
const currentProduct = ref<Partial<Product>>({
  status: true
});
const currentSkus = ref<Sku[]>([]);
const currentSku = ref<Partial<Sku>>({});
const editingSkuIndex = ref(-1);
const modalMode = ref<'create' | 'edit'>('create');

// 分页
const pagination = ref({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50]
});

// 数据
const products = ref<Product[]>([]);
const categories = ref<Category[]>([]);
const brands = ref<Brand[]>([]);

// 表单引用
const formRef = ref();
const skuFormRef = ref();

// 商品表单校验规则
const rules = {
  name: {
    required: true,
    message: '请输入商品名称',
    trigger: ['input', 'blur']
  },
  category_id: {
    required: true,
    type: 'number',
    message: '请选择分类',
    trigger: ['change']
  },
  brand_id: {
    required: true,
    type: 'number',
    message: '请选择品牌',
    trigger: ['change']
  }
};

// SKU表单校验规则
const skuRules = {
  spec: {
    required: true,
    message: '请输入规格描述',
    trigger: ['input', 'blur']
  },
  price: {
    required: true,
    type: 'number',
    min: 0,
    message: '请输入价格且不小于0',
    trigger: ['input', 'blur']
  },
  stock: {
    required: true,
    type: 'number',
    min: 0,
    message: '请输入库存且不小于0',
    trigger: ['input', 'blur']
  }
};

// 商品表格列定义
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 80
  },
  {
    title: '商品名称',
    key: 'name'
  },
  {
    title: '主图',
    key: 'cover_image',
    render(row: Product) {
      return h(NImage, {
        width: 60,
        src: row.cover_image,
        alt: row.name
      });
    }
  },
  {
    title: '分类',
    key: 'category_id',
    render(row: Product) {
      const category = categories.value.find(c => c.id === row.category_id);
      return category ? category.name : '-';
    }
  },
  {
    title: '品牌',
    key: 'brand_id',
    render(row: Product) {
      const brand = brands.value.find(b => b.id === row.brand_id);
      return brand ? brand.name : '-';
    }
  },
  {
    title: '状态',
    key: 'status',
    render(row: Product) {
      return h(NSwitch, {
        value: row.status,
        disabled: true,
        round: false
      }, {
        checked: () => '启用',
        unchecked: () => '禁用'
      });
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    render(row: Product) {
      return new Date(row.created_at).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).replace(/\//g, '-');
    }
  },
  {
    title: '操作',
    key: 'actions',
    render(row: Product) {
      return [
        h(NButton, {
          size: 'small',
          onClick: () => showProductModal(row, 'edit'),
          style: 'margin-right: 10px;'
        }, { default: () => '编辑' }),
        h(NButton, {
          size: 'small',
          type: 'error',
          onClick: () => deleteProduct(row.id)
        }, { default: () => '删除' })
      ];
    }
  }
];

// SKU表格列定义
const skuColumns = [
  {
    title: '规格',
    key: 'spec'
  },
  {
    title: '价格',
    key: 'price',
    render(row: Sku) {
      return `¥${(row.price / 100).toFixed(2)}`;
    }
  },
  {
    title: '库存',
    key: 'stock'
  },
  {
    title: '操作',
    key: 'actions',
    render(row: Sku, index: number) {
      return [
        h(NButton, {
          size: 'small',
          onClick: () => editSku(index),
          style: 'margin-right: 10px;'
        }, { default: () => '编辑' }),
        h(NButton, {
          size: 'small',
          type: 'error',
          onClick: () => removeSku(index)
        }, { default: () => '删除' })
      ];
    }
  }
];

// 处理分页变化
const handlePageChange = (page: number) => {
  pagination.value.page = page;
  fetchProducts();
};

// 处理搜索
const handleSearch = () => {
  pagination.value.page = 1;
  fetchProducts();
};

// 删除商品
const deleteProduct = (id: number) => {
  // 这里应该有一个确认对话框
  if (window.confirm('确定要删除这个商品吗？')) {
    axios.delete(`/api/v1/product-catalog/products/${id}`)
      .then(() => {
        message.success('删除成功');
        fetchProducts();
      })
      .catch(() => {
        message.error('删除失败');
      });
  }
};

// 获取商品列表
const fetchProducts = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/api/v1/product-catalog/products', {
      params: {
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        name: searchForm.value.name,
        category_id: searchForm.value.category_id,
        brand_id: searchForm.value.brand_id,
        status: searchForm.value.status
      }
    });
    
    products.value = response.data.items || response.data.data || response.data || [];
    pagination.value.itemCount = response.data.total || response.data.count || 0;
  } catch (error) {
    console.error('获取商品列表失败:', error);
    message.error('获取商品列表失败');
    products.value = []; // 确保在出错时设置为空数组
  } finally {
    loading.value = false;
  }
};

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/v1/product-catalog/categories');
    categories.value = response.data.items || response.data.data || response.data || [];
  } catch (error) {
    console.error('获取分类列表失败:', error);
    message.error('获取分类列表失败');
  }
};

// 获取品牌列表
const fetchBrands = async () => {
  try {
    const response = await axios.get('/api/v1/product-catalog/brands');
    brands.value = response.data.items || response.data.data || response.data || [];
  } catch (error) {
    console.error('获取品牌列表失败:', error);
    message.error('获取品牌列表失败');
  }
};

onMounted(() => {
  fetchProducts();
  fetchCategories();
  fetchBrands();
});

// 显示商品模态框
const showProductModal = (product: Partial<Product>, mode: 'create' | 'edit') => {
  modalMode.value = mode;
  
  if (mode === 'create') {
    currentProduct.value = { status: true };
    currentSkus.value = [];
  } else {
    currentProduct.value = { ...product };
    // 获取该商品的SKU列表
    fetchSkus(product.id!);
  }
  
  showModal.value = true;
};

// 获取SKU列表
const fetchSkus = async (productId: number) => {
  try {
    const response = await axios.get(`/api/v1/product-catalog/products/${productId}/skus`);
    currentSkus.value = response.data;
  } catch (error) {
    message.error('获取SKU列表失败');
    console.error(error);
  }
};

// 添加新SKU
const addNewSku = () => {
  currentSku.value = {};
  editingSkuIndex.value = -1;
  showSkuModal.value = true;
};

// 编辑SKU
const editSku = (index: number) => {
  currentSku.value = { ...currentSkus.value[index] };
  editingSkuIndex.value = index;
  showSkuModal.value = true;
};

// 删除SKU
const removeSku = (index: number) => {
  currentSkus.value.splice(index, 1);
};

// 保存SKU
const saveSku = (e: Event) => {
  e.preventDefault();
  skuFormRef.value?.validate(async (errors: any) => {
    if (!errors) {
      if (editingSkuIndex.value >= 0) {
        // 编辑现有的SKU
        currentSkus.value[editingSkuIndex.value] = { ...currentSku.value } as Sku;
      } else {
        // 添加新的SKU
        currentSkus.value.push({ ...currentSku.value } as Sku);
      }
      showSkuModal.value = false;
    }
  });
};

// 提交商品
const submitProduct = (e: Event) => {
  e.preventDefault();
  formRef.value?.validate(async (errors: any) => {
    if (!errors) {
      submitting.value = true;
      try {
        let productId: number;
        
        if (modalMode.value === 'create') {
          // 创建商品
          const response = await axios.post('/api/v1/product-catalog/products', currentProduct.value);
          productId = response.data.id;
          message.success('创建商品成功');
        } else {
          // 更新商品
          const response = await axios.put(
            `/api/v1/product-catalog/products/${currentProduct.value.id}`, 
            currentProduct.value
          );
          productId = currentProduct.value.id!;
          message.success('更新商品成功');
        }
        
        // 处理SKU
        await Promise.all(currentSkus.value.map(async (sku) => {
          const skuData = { ...sku, product_id: productId };
          if (sku.id) {
            // 更新SKU
            return axios.put(`/api/v1/product-catalog/skus/${sku.id}`, skuData);
          } else {
            // 创建SKU
            return axios.post('/api/v1/product-catalog/skus', skuData);
          }
        }));
        
        showModal.value = false;
        fetchProducts();
      } catch (error) {
        message.error(modalMode.value === 'create' ? '创建商品失败' : '更新商品失败');
        console.error(error);
      } finally {
        submitting.value = false;
      }
    }
  });
};

</script>

<style scoped>
.product-list {
  padding: 20px;
}

.actions {
  margin: 20px 0;
}

.sku-section {
  margin-top: 20px;
}
</style>