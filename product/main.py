from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute

from decouple import config
# Initialize FastAPI app
app = FastAPI()

# Define the PynamoDB Model for the Product table
class ProductModel(Model):
    class Meta:
        table_name = "Product"
        region = config('AWS_REGION')
        host = config('DATABASE_HOST')

        
        if config('ENVIRONMENT') == 'local':
            host = config('DATABASE_HOST')
            
    id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    price = NumberAttribute()

# Define the Pydantic Schema for Product
class ProductSchema(BaseModel):
    id: str
    name: str
    price: float

class ProductUpdateSchema(BaseModel):
    id: str
    name: Optional[str] = None
    price: Optional[float] = None

# Ensure the table is created
@app.on_event("startup")
async def on_startup():
    if not ProductModel.exists():
        ProductModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        print("Product Table created")


### CRUD Operations ###
@app.get("/products/")
async def list_products(limit: int = 10, offset: int = 0):
    try:
        # Fetch all items from the DynamoDB table
        items = list(ProductModel.scan())
        
        # Apply offset and limit for pagination
        paginated_items = items[offset: offset + limit]

        # Convert each PynamoDB item to a dictionary
        product_list = [
            {"id": item.id, "name": item.name, "price": item.price}
            for item in paginated_items
        ]

        return {
            "total": len(items),  # Total number of products
            "limit": limit,
            "offset": offset,
            "products": product_list
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Create a product
@app.post("/product/", response_model=ProductSchema)
async def create_product(product: ProductSchema):
    try:
        item = ProductModel(
            id=product.id,
            name=product.name,
            price=product.price
        )
        item.save()
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read a product by ID
@app.get("/product/{product_id}", response_model=ProductSchema)
async def get_product(product_id: str):
    try:
        item = ProductModel.get(product_id)
        return ProductSchema(id=item.id, name=item.name, price=item.price)
    except ProductModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

# Update a product
@app.put("/product/", response_model=ProductSchema)
async def update_product(product: ProductUpdateSchema):
    try:
        item = ProductModel.get(product.id)
        if product.name:
            item.name = product.name
        if product.price:
            item.price = product.price
        item.save()
        return ProductSchema(id=item.id, name=item.name, price=item.price)
    except ProductModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete a product by ID
@app.delete("/product/{product_id}")
async def delete_product(product_id: str):
    try:
        item = ProductModel.get(product_id)
        item.delete()
        return {"message": "Product deleted successfully"}
    except ProductModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


### Bulk Operations ###

# Bulk create products
# @app.post("/bulk-insert/")
# async def bulk_insert_products(products: List[ProductSchema]):
#     try:
#         with ProductModel.batch_write() as batch:
#             for product in products:
#                 item = ProductModel(
#                     id=product.id,
#                     name=product.name,
#                     price=product.price
#                 )
#                 batch.save(item)
#         return {"message": "Bulk insert successful!"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


async def set_create_attributes(item, data):
    for field, value in data.items():
        if value is not None:
            setattr(item, field, value)
    return item        

async def set_update_attributes(item, data):
    for field, value in data.items():
        if value is not None and field != "id":
            setattr(item, field, value)
    return item

    

@app.post("/bulk-insert/")
async def bulk_insert_products(products: List[ProductSchema]):
    errors = []  # To store any errors encountered during the process
    try:
        with ProductModel.batch_write() as batch:
            for i,product in enumerate(products):
                try:
                
                    # Create a new product item
                    item = ProductModel()
                    
                    # Set attributes dynamically from the product data
                    create_data = vars(product)
                    item = await set_create_attributes(item, create_data)
                    
                    # for field, value in create_data.items():
                    #     if value is not None:  # Only set non-None values
                    #         setattr(item, field, value)

                    # Save the new item to the batch
                    batch.save(item)
                    
                except Exception as e:
                    # Capture individual item errors
                    errors.append({"product": product.dict(), "error": str(e)})

        if errors:
            return {"message": "Bulk insert completed with some errors", "errors": errors}
        return {"message": "Bulk insert successful!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Bulk update products
@app.put("/bulk-update/")
async def bulk_update_products(products: List[ProductUpdateSchema]):
    errors = []  # To store any errors encountered during the process
    try:
        with ProductModel.batch_write() as batch:
            for product in products:
                try:
                    # Fetch the item from the database
                    item = ProductModel.get(product.id)

                    # Update the fields dynamically
                    update_data = vars(product)
                    item = await set_update_attributes(item, update_data)
                    # for field, value in update_data.items():
                    #     if value is not None and field != "id":  # Skip updating 'id'
                    #         setattr(item, field, value)

                    # Save the updated item to the batch
                    batch.save(item)
                    
                except ProductModel.DoesNotExist:
                    errors.append({"product_id": product.id, "error": "Product not found"})
                except Exception as e:
                    errors.append({"product_id": product.id, "error": str(e)})

        if errors:
            return {"message": "Bulk update completed with some errors", "errors": errors}
        return {"message": "Bulk update successful!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    
# Bulk delete products
@app.delete("/bulk-delete/")
async def bulk_delete_products(product_ids: List[str]):
    try:
        with ProductModel.batch_write() as batch:
            for product_id in product_ids:
                item = ProductModel.get(product_id)
                batch.delete(item)
        return {"message": "Bulk delete successful!"}
    except ProductModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="One or more products not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.on_event("startup")
async def on_startup():
    print("STARTED........")



@app.on_event("shutdown")
async def shutdown_event():
    # Stop the Kafka producer when FastAPI shuts down
    print("Stopped........")
