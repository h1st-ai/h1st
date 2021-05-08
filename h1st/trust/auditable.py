class Auditable:
    """
    A *Trustworthy-AI* interface that defines the capabilities of objects (e.g., `Models`, `Graphs`)
    that can self-record and report an audit trail of their activities and input/output artifacts.
    For example, an `Auditable` `Model` should be able to record and even retain its training data set,
    the training data scientist, the timestamp, model metrics, etc. available for query at any time in
    the future.
    """

    @property
    def audit_trailing(self):
        return getattr(self, "__audit_trailing", False)

    @audit_trailing.setter
    def audit_trailing(self, value):
        setattr(self, "__audit_trailing", value)

    def audit_trail_get(self, key):
        pass # to be implemented

    def audit_trail_set(self, key, value):
        if not self.audit_trailing: return
        # to be implemented

    def audit_trail_delete(self, key):
        pass # to be implemented