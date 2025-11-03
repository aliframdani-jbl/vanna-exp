from typing import Dict, Any


class TrainingManager:
    """Manages training operations for the Vanna model"""
    
    def __init__(self, vn_client, db_client):
        self.vn = vn_client
        self.db_client = db_client
    
    def train_ddl(self, ddl: str):
        """Train the model with DDL statements"""
        try:
            self.vn.train(ddl=ddl)
            return {"status": "success", "message": "DDL trained successfully"}
        except Exception as e:
            raise Exception(f"Failed to train DDL: {str(e)}")
    
    def train_documentation(self, documentation: str):
        """Train the model with documentation"""
        try:
            self.vn.train(documentation=documentation)
            return {"status": "success", "message": "Documentation trained successfully"}
        except Exception as e:
            raise Exception(f"Failed to train documentation: {str(e)}")
    
    def train_sql(self, question: str, sql: str):
        """Train the model with question-SQL pairs"""
        try:
            self.vn.train(question=question, sql=sql)
            return {"status": "success", "message": "Question-SQL pair trained successfully"}
        except Exception as e:
            raise Exception(f"Failed to train SQL: {str(e)}")
    
    def train_from_information_schema(self):
        """Train the model using database schema information"""
        try:
            # Get information schema from ClickHouse
            df_information_schema = self.db_client.get_schema_info()
            
            # Generate training plan
            plan = self.vn.get_training_plan_generic(df_information_schema)
            
            # Execute training
            self.vn.train(plan=plan)
            
            return {
                "status": "success", 
                "message": f"Schema training completed. Processed {len(df_information_schema)} columns.",
                "plan_items": len(plan) if plan else 0
            }
        except Exception as e:
            raise Exception(f"Failed to train from schema: {str(e)}")
    
    def get_training_data(self):
        """Get current training data"""
        try:
            raw_data = self.vn.get_training_data()
            
            # Check if raw_data is a pandas DataFrame
            if hasattr(raw_data, 'to_dict'):
                # It's a pandas DataFrame, convert to proper JSON format
                try:
                    # Convert DataFrame to list of dictionaries (records format)
                    training_records = raw_data.to_dict('records')
                    return training_records
                except Exception as df_error:
                    print(f"DEBUG: DataFrame conversion error: {df_error}")
                    # Fallback: convert to dictionary format
                    try:
                        return {
                            'columns': raw_data.columns.tolist(),
                            'data': raw_data.values.tolist(),
                            'index': raw_data.index.tolist()
                        }
                    except:
                        # Final fallback: convert to string but in a structured way
                        return {
                            'training_data_summary': f"Found {len(raw_data)} training records",
                            'columns': list(raw_data.columns) if hasattr(raw_data, 'columns') else [],
                            'row_count': len(raw_data) if hasattr(raw_data, '__len__') else 0,
                            'data_preview': str(raw_data.head() if hasattr(raw_data, 'head') else raw_data)
                        }
            
            # If it's a list, process each item
            elif isinstance(raw_data, list):
                serializable_data = []
                for item in raw_data:
                    if hasattr(item, '__dict__'):
                        # Convert object to dictionary
                        item_dict = {}
                        for key, value in vars(item).items():
                            try:
                                if isinstance(value, (str, int, float, bool, type(None))):
                                    item_dict[key] = value
                                elif isinstance(value, (list, dict)):
                                    item_dict[key] = value
                                else:
                                    item_dict[key] = str(value)
                            except:
                                item_dict[key] = str(value)
                        serializable_data.append(item_dict)
                    elif isinstance(item, dict):
                        # Already a dictionary, ensure values are serializable
                        clean_dict = {}
                        for key, value in item.items():
                            try:
                                if isinstance(value, (str, int, float, bool, type(None))):
                                    clean_dict[key] = value
                                elif isinstance(value, (list, dict)):
                                    clean_dict[key] = value
                                else:
                                    clean_dict[key] = str(value)
                            except:
                                clean_dict[key] = str(value)
                        serializable_data.append(clean_dict)
                    else:
                        serializable_data.append(str(item))
                return serializable_data
            
            # If it's a dictionary
            elif isinstance(raw_data, dict):
                clean_dict = {}
                for key, value in raw_data.items():
                    try:
                        if isinstance(value, (str, int, float, bool, type(None))):
                            clean_dict[key] = value
                        elif isinstance(value, (list, dict)):
                            clean_dict[key] = value
                        else:
                            clean_dict[key] = str(value)
                    except:
                        clean_dict[key] = str(value)
                return clean_dict
            
            # Fallback for other types
            else:
                return {
                    'training_data_type': str(type(raw_data)),
                    'training_data_summary': str(raw_data)[:500] + '...' if len(str(raw_data)) > 500 else str(raw_data)
                }
            
        except Exception as e:
            print(f"DEBUG: Error in get_training_data: {e}")
            raise Exception(f"Failed to get training data: {str(e)}")
    
    def remove_training_data(self, id: str):
        """Remove training data by ID"""
        try:
            self.vn.remove_training_data(id)
            return {"status": "success", "message": f"Training data {id} removed successfully"}
        except Exception as e:
            raise Exception(f"Failed to remove training data: {str(e)}")