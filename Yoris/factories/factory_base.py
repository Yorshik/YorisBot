import importlib
import pathlib
import pkgutil


class Factory:
    def _auto_register(self, package_name: str, base_class, factory_type: str = None):
        package = importlib.import_module(package_name)
        package_path = pathlib.Path(package.__file__).parent

        for finder, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
            module = importlib.import_module(f"{package_name}.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                        isinstance(attr, type)
                        and issubclass(attr, base_class)
                        and attr is not base_class
                ):
                    if factory_type is None or getattr(attr, "factory_type", None) == factory_type:
                        self.register(attr)

    def register(self, base_class):
        raise NotImplementedError
